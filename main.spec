# -*- mode: python ; coding: utf-8 -*-


import os

project_root = os.path.abspath(os.path.dirname(__file__))

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    # Only include app code and required non-Python files if any
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Exclude tests and documentation/info files
    excludes=['tests', 'info'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
