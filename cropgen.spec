# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cropgen.py'],
    pathex=[],
    binaries=[],
    # Forward slashes so the spec works on any build host. 'templates' must be here: the C++
    # code generator loads the jinja files through resource_path(), which reads from the
    # PyInstaller bundle at runtime -- without this entry that path works from source and
    # fails only in the built exe.
    datas=[
        ('operations.json', '.'),
        ('conditions.json', '.'),
        ('templates', 'templates'),
    ],
    hiddenimports=[],
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
    name='cropgen',
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
)
