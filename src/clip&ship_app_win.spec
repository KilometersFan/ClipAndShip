# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clipnship.py'],
             pathex=['..\\cns\\Lib\\site-packages', 'C:\\Users\\milop\\Projects\\ClipAndShip\\src'],
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
                    ('..\\cns\\Lib\\site-packages\\m3u8', 'm3u8'),
                    ('..\\cns\\Lib\\site-packages\\m3u8', 'twitchdl\\m3u8'),
                    ('..\\cns\\Lib\\site-packages\\iso8601\\', 'twitchdl\\iso8601\\'),
                    ('..\\cns\\Lib\\site-packages\\requests\\', 'twitchdl\\requests\\'),
                    ('..\\cns\\Lib\\site-packages\\urllib3\\', 'twitchdl\\urllib3\\'),
                    ('..\\cns\\Lib\\site-packages\\chardet\\', 'twitchdl\\chardet\\'),
                    ('..\\cns\\Lib\\site-packages\\certifi\\', 'twitchdl\\certifi\\'),
                    ('..\\cns\\Lib\\site-packages\\idna\\', 'twitchdl\\idna\\'),
                    ('..\\ffmpeg.exe', 'twitchdl\\ffmpeg'),
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
          console=False , icon='web\\favicon.ico')
app = BUNDLE(exe,
             name='clipnship.app',
             icon='web\\favicon.ico',
             bundle_identifier=None)
python -m eel clipnship.py web -i web\\favicon.ico --add-data="models\\*;models\\" --add-data="twitchdl\\*;twitchdl\\" --add-data="__init__.py;." --add-data="config.ini;." --add-data="channels.ini;." --onefile --noconsole --additional-hooks-dir="hooks" --add-data="..\\cns\\Lib\\site-packages\\kaleido;kaleido" --add-data="..\\cns\\Lib\\site-packages\\m3u8;m3u8" --add-data="..\\cns\\Lib\\site-packages\\m3u8;twitchdl\\m3u8" --add-data="..\\cns\\Lib\\site-packages\\iso8601\\;twitchdl\\iso8601\\" --add-data="..\\cns\\Lib\\site-packages\\requests\\;twitchdl\\requests\\" --add-data="..\\cns\\Lib\\site-packages\\urllib3\\;twitchdl\\urllib3\\" --add-data="..\\cns\\Lib\\site-packages\\chardet\\;twitchdl\\chardet" --add-data="..\\cns\\Lib\\site-packages\\certifi\\;twitchdl\\certifi\\" --add-data="..\\cns\\Lib\\site-packages\\idna\\;twitchdl\\idna\\" --add-data="..\\ffmpeg.exe;twitchdl\\ffmpeg"