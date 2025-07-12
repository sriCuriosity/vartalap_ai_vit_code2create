Write-Host "Building Business Management Software Executable..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install/upgrade required packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller main.spec --clean

# Check if build was successful
if (Test-Path "dist\BusinessManagement.exe") {
    Write-Host ""
    Write-Host "SUCCESS! Executable created successfully." -ForegroundColor Green
    Write-Host "Location: dist\BusinessManagement.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run the application by double-clicking BusinessManagement.exe" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to create executable" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
}

Read-Host "Press Enter to exit" 