@echo off
echo =================================================================
echo  CivicPulse - Citizen Complaint Management System
echo =================================================================
echo.
echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
echo.
echo Running automated verification tests...
python test_app.py
echo.
echo Starting application server at http://127.0.0.1:5000...
echo (Press Ctrl+C to stop the server)
echo.
python app.py
pause
