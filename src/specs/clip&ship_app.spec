# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clipnship.py'],
             pathex=['../cns/lib/python3.8/site-packages', '../src'],
             binaries=[],
             datas=[
                ('../cns/lib/python3.8/site-packages/eel/eel.js', 'eel'),
                ('web', 'web'),
                ('models/*', 'models/'),
                ('twitchdl/*', 'twitchdl/'),
                ('__init__.py', '__init__.py'),
                ('config.ini', '.'),
                ('channels.ini', '.'),
                ('../cns/lib/python3.8/site-packages/kaleido', 'kaleido'),
                ('../cns/lib/python3.8/site-packages/m3u8', 'm3u8'),
                ('../cns/lib/python3.8/site-packages/m3u8', 'twitchdl/m3u8'),
                ('../cns/lib/python3.8/site-packages/iso8601/', 'twitchdl/iso8601/'),
                ('../cns/lib/python3.8/site-packages/requests/', 'twitchdl/requests/'),
                ('../cns/lib/python3.8/site-packages/urllib3/', 'twitchdl/urllib3/'),
                ('../cns/lib/python3.8/site-packages/chardet/', 'twitchdl/chardet/'),
                ('../cns/lib/python3.8/site-packages/certifi/', 'twitchdl/certifi/'),
                ('../cns/lib/python3.8/site-packages/idna/', 'twitchdl/idna/'),
                ('../ffmpeg', 'twitchdl/ffmpeg'),
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
          console=False , icon='web/logo.png')
app = BUNDLE(exe,
             name='clipnship.app',
             icon='web/logo.png',
             bundle_identifier=None)
