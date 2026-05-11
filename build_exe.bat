@echo off
echo [MainGodSpace Builder] Starting build process...

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt

:: Check for pyinstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] PyInstaller installation failed.
    pause
    exit /b 1
)

:: Run pyinstaller
echo [2/3] Building executable using MainGodSpace_GUI.spec...
pyinstaller --noconfirm MainGodSpace_GUI.spec

if %errorlevel% neq 0 (
    echo [Error] PyInstaller build failed.
    pause
    exit /b 1
)

echo [3/3] Build complete! Check the 'dist' folder for MainGodSpace_GUI.exe.
echo Note: Ensure 'data', 'save', and other runtime folders are available next to the exe if not bundled.
pause
