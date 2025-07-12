@echo off
echo Building Business Management Software Executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install/upgrade required packages
echo Installing required packages...
pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Building executable...
pyinstaller main.spec --clean

REM Check if build was successful
if exist "dist\BusinessManagement.exe" (
    echo.
    echo SUCCESS! Executable created successfully.
    echo Location: dist\BusinessManagement.exe
    echo.
    echo You can now run the application by double-clicking BusinessManagement.exe
) else (
    echo.
    echo ERROR: Failed to create executable
    echo Please check the error messages above.
)

pause 