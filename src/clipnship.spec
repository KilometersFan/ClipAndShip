# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clipnship.py'],
             pathex=['../twitch-app/lib/python3.8/site-packages', '/Users/milesphan/Projects/TwitchClipAnalyzer/src'],
             binaries=[],
             datas=[('/Users/milesphan/Projects/TwitchClipAnalyzer/twitch-app/lib/python3.8/site-packages/eel/eel.js', 'eel'), ('web', 'web'), ('clips', 'clips'), ('data', 'data'), ('models/*', 'models/'), ('twitchdl/*', 'twitchdl/'), ('vods', 'vods'), ('__init__.py', '__init__.py'), ('config.ini', '.'), ('channels.ini', '.'), ('../twitch-app/lib/python3.8/site-packages/kaleido', 'kaleido')],
             hiddenimports=['bottle_websocket', 'wheel', 'twine'],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='clipnship',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='web/clipnship_.png')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='clipnship')
