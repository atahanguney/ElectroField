@echo off
cd /d "%~dp0"
title ElectroField - 1D/2D/3D/4D Electromagnetics Workbench Launcher

echo =================================================================
echo   ELECTROFIELD - MULTI-DIMENSIONAL ELECTROMAGNETICS WORKBENCH
echo =================================================================
echo.
echo [1/2] Opening Interactive 3D/4D WebGL Lab and 250-Question Bank...

if exist "index.html" (
explorer "index.html"
) else (
echo [WARNING] index.html not found in this folder!
)

echo.
echo [2/2] Checking for Python solver (ElectroField.py)...
where python >nul 2>&1
if %errorlevel% equ 0 (
echo Python detected! Running numerical solver and 3D Matplotlib plot...
python "ElectroField.py"
) else (
echo Python is not installed on this PC.
echo The 3D/4D WebGL Lab is now open in your web browser!
)
echo.
pause
