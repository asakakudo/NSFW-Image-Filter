# pyinstaller spec example -- adapt as needed
# pyinstaller --onefile --windowed build/pyinstaller.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis([
    'app/main.py',
],
    pathex=[],
    binaries=[],
    datas=[('app/themes/*', 'app/themes'), ('app/i18n/*', 'app/i18n')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='nsfw-separator', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='nsfw-separator')