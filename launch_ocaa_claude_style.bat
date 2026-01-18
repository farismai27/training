@echo off
REM OCAA Web UI - Claude Style
REM Matches claude.ai UI design

echo.
echo ======================================================================
echo  OCAA - Claude Style UI
echo ======================================================================
echo.
echo  Matching claude.ai design:
echo    * Clean, minimalist interface
echo    * User messages on the right (dark bubbles)
echo    * Assistant messages on the left with avatar
echo    * Proper code highlighting
echo    * Smooth animations
echo.

REM Check if API key is set
if "%ANTHROPIC_API_KEY%"=="" (
    echo Warning: ANTHROPIC_API_KEY not set
    echo You'll need to enter it in the sidebar
    echo.
    pause
)

REM Launch the UI
echo Starting OCAA Claude Style UI...
echo.
echo Open your browser to: http://localhost:8501
echo.

streamlit run ocaa_web_ui_claude_style.py

pause
