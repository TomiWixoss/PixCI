# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('.palette_cache', '.palette_cache'), ('pixci-web\\backend\\pixci', 'pixci')]
binaries = []
hiddenimports = ['typer', 'rich', 'rich.console', 'pixci', 'pixci.cli', 'pixci.core', 'pixci.core.canvas', 'pixci.core.animation', 'pixci.core.grid_engine', 'pixci.core.code_engine', 'pixci.core.pxvg_engine', 'pixci.core.prompts', 'pixci.core.mixins', 'pixci.core.mixins.color', 'pixci.styles', 'pixci.styles.minecraft']
tmp_ret = collect_all('typer')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['pixci_cli_entry.py'],
    pathex=['pixci-web\\backend'],
    binaries=binaries,
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
    name='pixci-cli',
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
