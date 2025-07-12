# Building Windows Executable for Business Management Software

This guide will help you create a standalone Windows executable (.exe) file for the Business Management Software.

## Prerequisites

1. **Python 3.7 or higher** installed on your Windows system
2. **pip** (Python package installer) should be available
3. **Git** (optional, for cloning the repository)

## Method 1: Using the Automated Scripts (Recommended)

### Option A: Using Batch File (Windows Command Prompt)
1. Open Command Prompt in the project directory
2. Run: `build_exe.bat`
3. Wait for the build process to complete
4. The executable will be created in the `dist` folder

### Option B: Using PowerShell Script
1. Open PowerShell in the project directory
2. Run: `.\build_exe.ps1`
3. Wait for the build process to complete
4. The executable will be created in the `dist` folder

## Method 2: Manual Build Process

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Build the Executable
```bash
pyinstaller main.spec --clean
```

### Step 3: Locate the Executable
The executable will be created at: `dist\BusinessManagement.exe`

## What's Included in the Executable

The executable includes:
- All Python dependencies (PyQt5, pandas, numpy, matplotlib, etc.)
- The complete business_management module
- Database file (bills.db)
- Configuration files (Bill Number.txt)
- Application icon (icon.ico)

## Running the Application

1. Navigate to the `dist` folder
2. Double-click `BusinessManagement.exe`
3. The application will start with a graphical interface

## Troubleshooting

### Common Issues:

1. **"Python not found" error**
   - Ensure Python is installed and added to PATH
   - Try running `python --version` in command prompt

2. **Missing dependencies**
   - Run `pip install -r requirements.txt` manually
   - Ensure you have internet connection for downloading packages

3. **Large executable size**
   - This is normal for PyQt5 applications
   - The executable includes all necessary libraries

4. **Antivirus warnings**
   - Some antivirus software may flag PyInstaller executables
   - Add the dist folder to your antivirus exclusions

5. **Application crashes on startup**
   - Check if all required files are present in the dist folder
   - Ensure the database file (bills.db) is included

### File Structure After Build:
```
dist/
├── BusinessManagement.exe
├── business_management/
│   ├── ui/
│   ├── models/
│   ├── database/
│   └── ...
├── bills.db
├── Bill Number.txt
└── icon.ico
```

## Distribution

To distribute the application:
1. Copy the entire `dist` folder
2. Share the folder with users
3. Users can run `BusinessManagement.exe` directly

## Notes

- The executable is self-contained and doesn't require Python installation on target machines
- The build process may take several minutes depending on your system
- The final executable size will be around 100-200 MB due to included libraries
- Make sure to test the executable on a clean Windows machine before distribution

## Support

If you encounter issues during the build process:
1. Check that all prerequisites are met
2. Ensure you have sufficient disk space (at least 1GB free)
3. Try running the build process as administrator
4. Check the console output for specific error messages 