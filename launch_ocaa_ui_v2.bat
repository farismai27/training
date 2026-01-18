@echo off
REM OCAA Web UI v2 Launcher - Enhanced with AI SDK Patterns
REM Starts the improved OCAA Streamlit interface

echo.
echo ======================================================================
echo  Starting OCAA Web UI v2 - Enhanced with AI SDK Patterns
echo ======================================================================
echo.
echo New Features:
echo   * Streaming responses in real-time
echo   * Tool use visualization
echo   * Message artifacts
echo   * Token usage tracking
echo   * Enhanced error handling
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
    echo Installing Streamlit and Anthropic...
    pip install streamlit anthropic
)

REM Launch the UI
echo Starting OCAA Web UI v2...
echo.
echo Once started, open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run ocaa_web_ui_v2.py

pause
