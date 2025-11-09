#!/usr/bin/env python3
"""
Test script for MediTrack system
"""
import requests
import json
import time
import subprocess
import sys
import os

def test_ml_service():
    """Test the ML service directly"""
    print("Testing ML Service...")
    
    # Test data
    test_data = {
        "report_type": "Blood",
        "parameters": {
            "Hemoglobin (Hb)": 14.5,
            "RBC Count": 4.8,
            "WBC Count": 7500
        },
        "gender": "Male"
    }
    
    try:
        response = requests.post("http://localhost:8000/analyze", json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ ML Service working!")
            print(f"   Overall Status: {result['overall_status']}")
            print(f"   Overall Score: {result['overall_score']}")
            print(f"   Parameters analyzed: {len(result['parameter_analyses'])}")
            return True
        else:
            print(f"❌ ML Service error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ML Service not running on port 8000")
        return False
    except Exception as e:
        print(f"❌ ML Service error: {e}")
        return False

def test_web_server():
    """Test the web server"""
    print("\nTesting Web Server...")
    
    try:
        response = requests.get("http://localhost:4000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Web Server working!")
            return True
        else:
            print(f"❌ Web Server error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Web Server not running on port 4000")
        return False
    except Exception as e:
        print(f"❌ Web Server error: {e}")
        return False

def test_analysis_endpoint():
    """Test the analysis endpoint through web server"""
    print("\nTesting Analysis Endpoint...")
    
    test_data = {
        "report_type": "Sugar",
        "parameters": {
            "Fasting Blood Sugar (FBS)": 95,
            "Post-Meal (PPBS)": 120
        },
        "gender": "Female"
    }
    
    try:
        response = requests.post("http://localhost:4000/api/analysis/analyze", json=test_data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis Endpoint working!")
            print(f"   Report Type: {result['report_type']}")
            print(f"   Overall Status: {result['overall_status']}")
            print(f"   Summary: {result['summary'][:100]}...")
            return True
        else:
            print(f"❌ Analysis Endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Analysis Endpoint not accessible")
        return False
    except Exception as e:
        print(f"❌ Analysis Endpoint error: {e}")
        return False

def main():
    print("🏥 MediTrack System Test")
    print("=" * 50)
    
    # Check if services are running
    ml_ok = test_ml_service()
    web_ok = test_web_server()
    
    if ml_ok and web_ok:
        analysis_ok = test_analysis_endpoint()
        
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print(f"   ML Service: {'✅ PASS' if ml_ok else '❌ FAIL'}")
        print(f"   Web Server: {'✅ PASS' if web_ok else '❌ FAIL'}")
        print(f"   Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
        
        if ml_ok and web_ok and analysis_ok:
            print("\n🎉 All tests passed! System is ready to use.")
            print("\nTo use the system:")
            print("1. Open web_interface.html in your browser")
            print("2. Select a report type and enter values")
            print("3. Click 'Analyze My Report' to get results")
        else:
            print("\n⚠️  Some tests failed. Check the services are running.")
    else:
        print("\n❌ Services not running. Please start them first:")
        print("   - ML Service: cd ml_service && python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        print("   - Web Server: cd server && npm run dev")

if __name__ == "__main__":
    main()
