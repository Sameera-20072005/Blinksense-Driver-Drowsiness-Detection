@echo off
echo ========================================
echo   BlinkSense - Driver Drowsiness Detection
echo ========================================
echo.
echo Starting the application...
echo Please allow camera access when prompted!
echo.
echo Opening browser to http://localhost:5000
start http://localhost:5000
echo.
echo Starting BlinkSense server...
python blinksense_fixed.py
pause