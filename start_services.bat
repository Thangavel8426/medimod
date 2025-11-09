@echo off
echo Starting MediTrack Services...
echo.

echo Starting ML Service (Python FastAPI)...
start "ML Service" cmd /k "cd ml_service && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo Starting Web Server (Node.js)...
start "Web Server" cmd /k "cd server && npm run dev"

timeout /t 3 /nobreak > nul

echo Opening Web Interface...
start "" "web_interface.html"

echo.
echo Services started successfully!
echo - ML Service: http://localhost:8000
echo - Web Server: http://localhost:4000
echo - Web Interface: web_interface.html
echo.
echo Press any key to exit...
pause > nul
