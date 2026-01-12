@echo off
REM Launch Anthropic's Computer Use Reference Implementation
REM This provides the EXACT web UI from the lesson!

echo ==========================================
echo 🖥️  Anthropic Computer Use Reference
echo    Official Implementation with Web UI
echo ==========================================
echo.

REM Check for API key
if "%ANTHROPIC_API_KEY%"=="" (
    echo ❌ Error: ANTHROPIC_API_KEY not set
    echo.
    echo Please set your API key:
    echo   set ANTHROPIC_API_KEY=your-api-key-here
    echo.
    echo Or add to System Environment Variables
    echo.
    pause
    exit /b 1
)

echo ✅ API key found
echo.

REM Check for Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker not found
    echo.
    echo Please install Docker Desktop for Windows:
    echo   https://docs.docker.com/desktop/install/windows-install/
    echo.
    pause
    exit /b 1
)

echo ✅ Docker found
echo.

REM Pull the latest image
echo 📦 Pulling latest Computer Use image...
docker pull ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

echo.
echo ==========================================
echo 🚀 Starting Computer Use Demo
echo ==========================================
echo.
echo The web UI will be available at:
echo   http://localhost:8080
echo.
echo Press Ctrl+C to stop
echo.

REM Run the container
docker run ^
    -e ANTHROPIC_API_KEY=%ANTHROPIC_API_KEY% ^
    -v %USERPROFILE%\.anthropic:/home/computeruse/.anthropic ^
    -p 5900:5900 ^
    -p 8501:8501 ^
    -p 6080:6080 ^
    -p 8080:8080 ^
    -it ^
    --name computer-use-demo ^
    ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

REM Clean up on exit
docker rm computer-use-demo >nul 2>&1
