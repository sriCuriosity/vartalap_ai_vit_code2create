# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['business_management/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('business_management', 'business_management'), 
        ('Bill Number.txt', '.'),
        ('bills.db', '.'),
        ('icon.ico', '.'),
        # Add all .py files from prophet
        ('C:/Users/Admin/AppData/Local/Programs/Python/Python313/Lib/site-packages/prophet', 'prophet'),
        # Add matplotlib data (fonts, etc.)
        ('C:/Users/Admin/AppData/Local/Programs/Python/Python313/Lib/site-packages/matplotlib/mpl-data', 'mpl-data'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'pandas',
        'numpy',
        'matplotlib',
        'prophet',
        'fbprophet',
        'fuzzywuzzy',
        'fuzzywuzzy.process',
        'fuzzywuzzy.fuzz',
        'squarify',
        'sqlite3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BusinessManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
