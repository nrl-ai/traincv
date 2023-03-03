# -*- mode: python -*-
# vim: ft=python

import sys


sys.setrecursionlimit(5000)  # required on Windows


a = Analysis(
    ['traincv/app.py'],
    pathex=['traincv'],
    binaries=[],
    datas=[
       ('traincv/configs/labelme_config.yaml', 'traincv/views/labeling/labelme/config'),
       ('traincv/views/labeling/labelme/icons/*', 'traincv/views/labeling/labelme/icons'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='traincv',
    debug=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    #icon='traincv/icons/icon.ico',
)
app = BUNDLE(
    exe,
    name='traincv.app',
    #icon='traincv/icons/icon.icns',
    bundle_identifier=None,
    info_plist={'NSHighResolutionCapable': 'True'},
)