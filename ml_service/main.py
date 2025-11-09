from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, Literal, Dict, Any, List
import numpy as np
import pandas as pd
import json
import re
from datetime import datetime

app = FastAPI(title="MediTrack ML Service")

# Load health standards from Excel
def load_health_standards():
    try:
        df = pd.read_excel('../Health_Test_Report.xlsx')
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        # Fallback to JSON if Excel fails
        try:
            with open('../health_standards.json', 'r') as f:
                return json.load(f)
        except Exception as e2:
            print(f"Error loading JSON fallback: {e2}")
            return []

HEALTH_STANDARDS = load_health_standards()

class HealthReportIn(BaseModel):
    report_type: Literal["Blood", "Jaundice/ LFT", "Urine", "Sugar"]
    parameters: Dict[str, Any]
    gender: Optional[Literal["Male", "Female"]] = None

class ParameterAnalysis(BaseModel):
    parameter: str
    value: Any
    normal_range: str
    status: Literal["Normal", "Low", "High", "Critical"]
    interpretation: str
    recommendation: str
    score: float

class AnalysisOut(BaseModel):
    report_type: str
    overall_status: Literal["Good", "Needs Improvement", "Critical"]
    overall_score: float
    parameter_analyses: List[ParameterAnalysis]
    summary: str
    urgent_actions: List[str]
    general_recommendations: List[str]

def parse_normal_range(normal_range: str, gender: str = None) -> tuple:
    """Parse normal range string and return (min, max) values"""
    if pd.isna(normal_range) or normal_range is None:
        return None, None
    
    normal_range = str(normal_range).strip()
    
    # Handle gender-specific ranges
    if gender and ("Male:" in normal_range or "Female:" in normal_range):
        if gender == "Male" and "Male:" in normal_range:
            range_part = normal_range.split("Male:")[1].split(",")[0].strip()
        elif gender == "Female" and "Female:" in normal_range:
            range_part = normal_range.split("Female:")[1].split(",")[0].strip()
        else:
            return None, None
    else:
        range_part = normal_range
    
    # Handle different range formats
    if "<" in range_part:
        # Less than format (e.g., "<140 mg/dL")
        max_val = re.findall(r'<(\d+\.?\d*)', range_part)
        return None, float(max_val[0]) if max_val else None
    elif "-" in range_part:
        # Range format (e.g., "70-99 mg/dL")
        range_vals = re.findall(r'(\d+\.?\d*)-(\d+\.?\d*)', range_part)
        if range_vals:
            return float(range_vals[0][0]), float(range_vals[0][1])
    elif "Negative" in range_part:
        return 0, 0  # Special case for negative results
    
    return None, None

def analyze_parameter(parameter_name: str, value: Any, gender: str = None) -> ParameterAnalysis:
    """Analyze a single parameter against health standards"""
    
    # Find the parameter in standards
    standard = None
    for std in HEALTH_STANDARDS:
        if std['Parameter'].lower() == parameter_name.lower():
            standard = std
            break
    
    if not standard:
        return ParameterAnalysis(
            parameter=parameter_name,
            value=value,
            normal_range="Unknown",
            status="Unknown",
            interpretation="Parameter not found in standards",
            recommendation="Consult healthcare provider",
            score=0.5
        )
    
    # Parse normal range
    min_val, max_val = parse_normal_range(standard['Normal Range'], gender)
    
    # Handle special cases
    if "Negative" in str(standard['Normal Range']):
        if value == 0 or value == "Negative" or value is False:
            status = "Normal"
            score = 1.0
            interpretation = "Normal - No abnormality detected"
        else:
            status = "High"
            score = 0.2
            interpretation = standard.get('High / Low Indicates', 'Abnormal result detected')
    else:
        # Numeric analysis
        try:
            numeric_value = float(value)
            
            if min_val is None and max_val is not None:
                # Only max value (e.g., <140)
                if numeric_value <= max_val:
                    status = "Normal"
                    score = 1.0
                    interpretation = "Within normal range"
                else:
                    status = "High"
                    score = 0.2
                    interpretation = standard.get('High / Low Indicates', 'Above normal range')
            elif min_val is not None and max_val is not None:
                # Range analysis
                if min_val <= numeric_value <= max_val:
                    status = "Normal"
                    score = 1.0
                    interpretation = "Within normal range"
                elif numeric_value < min_val:
                    status = "Low"
                    score = 0.3
                    interpretation = standard.get('High / Low Indicates', 'Below normal range')
                else:
                    status = "High"
                    score = 0.3
                    interpretation = standard.get('High / Low Indicates', 'Above normal range')
            else:
                status = "Unknown"
                score = 0.5
                interpretation = "Unable to determine normal range"
                
        except (ValueError, TypeError):
            status = "Unknown"
            score = 0.5
            interpretation = "Invalid value format"
    
    # Determine if critical
    if status in ["High", "Low"] and score <= 0.3:
        status = "Critical"
    
    recommendation = standard.get('How to Improve / Manage', 'Consult healthcare provider')
    
    return ParameterAnalysis(
        parameter=parameter_name,
        value=value,
        normal_range=standard['Normal Range'],
        status=status,
        interpretation=interpretation,
        recommendation=recommendation,
        score=score
    )

def generate_analysis(report_type: str, parameters: Dict[str, Any], gender: str = None) -> AnalysisOut:
    """Generate comprehensive health analysis"""
    
    parameter_analyses = []
    urgent_actions = []
    general_recommendations = []
    
    # Analyze each parameter
    for param_name, value in parameters.items():
        if value is not None and value != "":
            analysis = analyze_parameter(param_name, value, gender)
            parameter_analyses.append(analysis)
            
            # Collect urgent actions and recommendations
            if analysis.status == "Critical":
                urgent_actions.append(f"{analysis.parameter}: {analysis.recommendation}")
            elif analysis.status in ["High", "Low"]:
                general_recommendations.append(f"{analysis.parameter}: {analysis.recommendation}")
    
    # Calculate overall score
    if parameter_analyses:
        overall_score = np.mean([p.score for p in parameter_analyses])
    else:
        overall_score = 0.5
    
    # Determine overall status
    if overall_score >= 0.8:
        overall_status = "Good"
    elif overall_score >= 0.5:
        overall_status = "Needs Improvement"
    else:
        overall_status = "Critical"
    
    # Generate summary
    normal_count = sum(1 for p in parameter_analyses if p.status == "Normal")
    abnormal_count = len(parameter_analyses) - normal_count
    
    if abnormal_count == 0:
        summary = f"All {len(parameter_analyses)} parameters are within normal range. Great job maintaining your health!"
    elif normal_count > abnormal_count:
        summary = f"Most parameters ({normal_count}/{len(parameter_analyses)}) are normal. {abnormal_count} parameter(s) need attention."
    else:
        summary = f"Several parameters ({abnormal_count}/{len(parameter_analyses)}) are outside normal range and require attention."
    
    return AnalysisOut(
        report_type=report_type,
        overall_status=overall_status,
        overall_score=round(overall_score, 2),
        parameter_analyses=parameter_analyses,
        summary=summary,
        urgent_actions=urgent_actions,
        general_recommendations=general_recommendations
    )

@app.get("/standards")
def get_health_standards():
    """Get available health standards by category"""
    categories = {}
    for std in HEALTH_STANDARDS:
        category = std['Category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'parameter': std['Parameter'],
            'normal_range': std['Normal Range'],
            'indicates': std['High / Low Indicates'],
            'management': std['How to Improve / Manage']
        })
    return categories

@app.post("/analyze", response_model=AnalysisOut)
def analyze_health_report(report: HealthReportIn):
    """Analyze health report against standards"""
    try:
        return generate_analysis(report.report_type, report.parameters, report.gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok", "standards_loaded": len(HEALTH_STANDARDS) > 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)