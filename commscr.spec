# -*- mode: python ; coding: utf-8 -*-

import string
import os


print(os.getcwd())


block_cipher = None


a = Analysis(['commscr.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['input.txt','output.txt','output.txt.tags.json','setup.jsom'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='commscr',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               Tree('my_idlelib','my_idlelib'),
               Tree('doc','doc'),
               Tree('scripts','scripts'),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='commscr')
