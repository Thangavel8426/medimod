# MediTrack - AI-Powered Health Report Analysis

A comprehensive health report analysis system that compares user input against medical standards from Excel data and provides intelligent feedback with historical tracking.

## Features

- 📊 **Multiple Report Types**: Blood tests, Liver Function Tests (LFT), Urine analysis, and Blood sugar tests
- 🤖 **AI Analysis**: Intelligent comparison against medical standards from Excel data
- 📈 **Historical Tracking**: Store and compare previous reports for trend analysis
- 💡 **Smart Recommendations**: Personalized health advice based on test results
- 🌐 **Web Interface**: User-friendly interface for easy data entry and result viewing

## Project Structure

```
medimod/
├── ml_service/           # Python FastAPI ML service
│   ├── main.py          # Main ML analysis logic
│   └── requirements.txt # Python dependencies
├── server/              # Node.js web server
│   ├── src/
│   │   ├── app.js       # Express app setup
│   │   ├── index.js     # Server entry point
│   │   ├── lib/db.js    # Database configuration
│   │   └── routes/      # API routes
│   └── package.json     # Node.js dependencies
├── Health_Test_Report.xlsx  # Medical standards data
├── web_interface.html   # Web user interface
└── start_services.bat   # Windows startup script
```

## Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- MySQL database (optional, for user authentication)

### Installation

1. **Install Python dependencies:**
   ```bash
   cd ml_service
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**
   ```bash
   cd server
   npm install
   ```

3. **Start the services:**
   - **Windows**: Double-click `start_services.bat`
   - **Manual**: 
     ```bash
     # Terminal 1 - ML Service
     cd ml_service
     python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
     
     # Terminal 2 - Web Server
     cd server
     npm run dev
     ```

4. **Open the web interface:**
   - Open `web_interface.html` in your browser
   - Or navigate to the file in your file explorer

## Usage

1. **Select Report Type**: Choose from Blood, LFT, Urine, or Sugar tests
2. **Enter Values**: Input your test results in the provided fields
3. **Get Analysis**: Click "Analyze My Report" to get AI-powered feedback
4. **View History**: See your previous reports and track improvements

## API Endpoints

### ML Service (Port 8000)
- `GET /health` - Service health check
- `GET /standards` - Get available health standards
- `POST /analyze` - Analyze health report

### Web Server (Port 4000)
- `GET /health` - Server health check
- `POST /api/analysis/analyze` - Analyze health report
- `GET /api/analysis/history` - Get analysis history (auth required)
- `GET /api/analysis/standards` - Get health standards

## Health Standards

The system uses medical standards from `Health_Test_Report.xlsx` including:

- **Blood Tests**: Hemoglobin, RBC, WBC, Platelets, Creatinine, Urea
- **Liver Function**: Bilirubin, ALT, AST, ALP, Albumin
- **Urine Analysis**: Glucose, Protein, Ketones, Blood cells
- **Blood Sugar**: Fasting, Post-meal, HbA1c

## Analysis Features

- **Status Classification**: Good, Needs Improvement, Critical
- **Parameter Analysis**: Individual parameter assessment
- **Recommendations**: Personalized health advice
- **Urgent Actions**: Critical alerts requiring immediate attention
- **Historical Comparison**: Track progress over time

## Database Schema

The system uses MySQL with the following tables:
- `users` - User authentication
- `reports` - Weekly health reports
- `health_analyses` - Detailed analysis results

## Development

### Adding New Parameters
1. Update `Health_Test_Report.xlsx` with new parameters
2. The ML service will automatically load new standards
3. Update the web interface parameter definitions if needed

### Customizing Analysis Logic
Edit `ml_service/main.py` to modify:
- Normal range parsing
- Status classification
- Recommendation generation

## Troubleshooting

- **ML Service not starting**: Check Python dependencies and port 8000 availability
- **Web Server errors**: Verify Node.js installation and port 4000 availability
- **Database errors**: Ensure MySQL is running and credentials are correct
- **Analysis failures**: Check that Excel file is accessible and properly formatted

## License

This project is created for educational purposes as part of an AI/ML course assignment.
