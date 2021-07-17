# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clipnship.py'],
             pathex=['../clipandship/lib/python3.8/site-packages', '../src'],
             binaries=[],
             datas=[
                ('../clipandship/lib/python3.8/site-packages/eel/eel.js', 'eel'),
                ('web', 'web'),
                ('models/*', 'models/'),
                ('twitchdl/*', 'twitchdl/'),
                ('__init__.py', '__init__.py'),
                ('config.ini', '.'),
                ('channels.ini', '.'),
                ('../clipandship/lib/python3.8/site-packages/kaleido', 'kaleido'),
                ('../clipandship/lib/python3.8/site-packages/m3u8', 'twitchdl/m3u8'),
                ('../clipandship/lib/python3.8/site-packages/iso8601/', 'twitchdl/iso8601/'),
                ('../clipandship/lib/python3.8/site-packages/requests/', 'twitchdl/requests/'),
                ('../clipandship/lib/python3.8/site-packages/urllib3/', 'twitchdl/urllib3/'),
                ('../clipandship/lib/python3.8/site-packages/chardet/', 'twitchdl/chardet/'),
                ('../clipandship/lib/python3.8/site-packages/certifi/', 'twitchdl/certifi/'),
                ('../clipandship/lib/python3.8/site-packages/idna/', 'twitchdl/idna/'),
            ],
             hiddenimports=['bottle_websocket', 'wheel', 'twine', 'm3u8'],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
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
          name='clipnship',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='web/logo.png')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='clipnship')
