@echo off
echo Starting BlinkSense - Driver Drowsiness Detection System
echo =====================================================
echo.
echo Opening browser to http://localhost:5000
start http://localhost:5000
echo.
echo Starting the application...
python drowsiness_web_app.py
pause