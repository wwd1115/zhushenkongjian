@echo off
echo [MainGodSpace Builder] Starting build process...

:: Check for python
set PYTHON_CMD=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set PYTHON_CMD=py
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [Error] Python is not installed or not in PATH.
        echo Please install Python from python.org and ensure 'Add to PATH' is checked.
        pause
        exit /b 1
    )
)

:: Install dependencies
echo [1/3] Installing dependencies using %PYTHON_CMD%...
%PYTHON_CMD% -m pip install -r requirements.txt

:: Check for pyinstaller
%PYTHON_CMD% -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] PyInstaller installation failed.
    pause
    exit /b 1
)

:: Run pyinstaller
echo [2/3] Building executable using MainGodSpace_GUI.spec...
%PYTHON_CMD% -m PyInstaller --noconfirm MainGodSpace_GUI.spec

if %errorlevel% neq 0 (
    echo [Error] PyInstaller build failed.
    pause
    exit /b 1
)

echo [3/3] Build complete! Check the 'dist' folder for MainGodSpace_GUI.exe.
echo Note: Ensure 'data', 'save', and other runtime folders are available next to the exe if not bundled.
pause
