# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clipnship.py'],
             pathex=['..\\cns\\Lib\\site-packages\\', '..\\src'],
             binaries=[],
             datas=[
                ('..\\cns\\Lib\\site-packages\\eel\\eel.js', 'eel'),
                ('web', 'web'),
                ('models\\*', 'models\\'),
                ('twitchdl\\*', 'twitchdl\\'),
                ('__init__.py', '__init__.py'),
                ('config.ini', '.'),
                ('channels.ini', '.'),
                ('..\\cns\\Lib\\site-packages\\kaleido', 'kaleido'),
                ('..\\cns\\Lib\\site-packages\\m3u8', 'm3u8')
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
          console=True , icon='web\\favicon.ico')
