@echo off
REM OCAA Web UI Launcher for Windows
REM Starts the custom OCAA Streamlit interface

echo.
echo ======================================================================
echo  Starting OCAA Web UI - OneSuite Core Architect Agent
echo ======================================================================
echo.

REM Check if API key is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo Warning: ANTHROPIC_API_KEY not set in environment
    echo You'll need to enter it in the web UI
    echo.
    echo To set it permanently:
    echo   setx ANTHROPIC_API_KEY "your-api-key-here"
    echo.
    pause
)

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing Streamlit...
    pip install streamlit
)

REM Launch the UI
echo Starting OCAA Web UI...
echo.
echo Once started, open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run ocaa_web_ui.py

pause
