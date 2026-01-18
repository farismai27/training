@echo off
REM OCAA Web UI - Dark Theme
REM Matches OneSuite dark UI design

echo.
echo ======================================================================
echo  OCAA - Dark Theme UI
echo ======================================================================
echo.
echo  Features:
echo    * Dark background with green accents
echo    * Left sidebar with menu
echo    * "New Chat" button
echo    * Projects, Artifacts, Knowledge Base
echo    * Centered welcome message
echo    * Modern, clean design
echo.

REM Launch the UI
echo Starting OCAA Dark Theme UI...
echo.
echo Open your browser to: http://localhost:8501
echo.

streamlit run ocaa_web_ui_dark.py

pause
