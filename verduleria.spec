# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/templates/*', 'src/templates'),
        ('src/static/**/*', 'src/static'),
        ('sql/schema_sqlite.sql', 'sql'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'bcrypt',
        'jwt',
        'sqlite3',
        'datetime',
        'random',
        'logging',
        'dotenv'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VerduleriaApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True para mostrar consola (útil para debug), False para ocultarla
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)