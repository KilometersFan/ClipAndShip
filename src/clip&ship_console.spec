# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clipnship.py'],
             pathex=['../cns/lib/python3.8/site-packages', '/Users/milesphan/Projects/TwitchClipAnalyzer/src'],
             binaries=[],
             datas=[
                ('/Users/milesphan/Projects/TwitchClipAnalyzer/cns/lib/python3.8/site-packages/eel/eel.js', 'eel'),
                ('web', 'web'),
                ('clips', 'clips'),
                ('data', 'data'),
                ('models/*', 'models/'),
                ('twitchdl/*', 'twitchdl/'),
                ('vods', 'vods'),
                ('__init__.py', '__init__.py'),
                ('config.ini', '.'),
                ('channels.ini', '.'),
                ('../cns/lib/python3.8/site-packages/kaleido', 'kaleido'),
                ('../cns/lib/python3.8/site-packages/m3u8', 'm3u8')
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='clipnship',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='web/logo.png')
