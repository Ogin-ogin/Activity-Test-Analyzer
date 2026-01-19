@echo off
chcp 65001 >nul

echo ========================================
echo Benzene Oxidation Activity Analysis
echo ========================================
echo.
echo Starting application...
echo.

cd /d "%~dp0"

streamlit run app.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start application.
    echo.
    pause
)
