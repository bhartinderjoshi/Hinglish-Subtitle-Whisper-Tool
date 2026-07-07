@echo off
echo ========================================
echo   Whisper Video-to-SRT Network Server
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo [1/3] Python detected
echo.

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found!
    echo Install from: https://ffmpeg.org/download.html
    pause
)

echo [2/3] FFmpeg detected
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP:~1%

echo [3/3] Starting server on network...
echo.
echo ========================================
echo   Server will be accessible at:
echo   - Local:   http://localhost:5000
echo   - Network: http://%IP%:5000
echo ========================================
echo.
echo Share the Network URL with others on your WiFi!
echo Press Ctrl+C to stop the server
echo.

REM Start server on all interfaces
python web_server.py --host 0.0.0.0 --port 5000

pause
