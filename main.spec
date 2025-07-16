# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [
    ('business_management', 'business_management'),
    ('Bill Number.txt', '.'),
    ('bills.db', '.'),
    ('icon.ico', '.'),
]
datas += collect_data_files('prophet')

hiddenimports = collect_submodules('prophet') + [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'pandas',
    'numpy',
    'matplotlib',
    'fbprophet',
    'fuzzywuzzy',
    'fuzzywuzzy.process',
    'fuzzywuzzy.fuzz',
    'squarify',
    'sqlite3'
]

a = Analysis(
    ['business_management/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
