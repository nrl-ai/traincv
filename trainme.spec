# -*- mode: python -*-
# vim: ft=python

import sys


sys.setrecursionlimit(5000)  # required on Windows


a = Analysis(
    ['trainme/app.py'],
    pathex=['trainme'],
    binaries=[],
    datas=[
       ('trainme/widgets/labeling/labelme/labelme/config/default_config.yaml', 'trainme/widgets/labeling/labelme/labelme/config'),
       ('trainme/widgets/labeling/labelme/labelme/icons/*', 'trainme/widgets/labeling/labelme/labelme/icons'),
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
    name='trainme',
    debug=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    #icon='trainme/icons/icon.ico',
)
app = BUNDLE(
    exe,
    name='trainme.app',
    #icon='trainme/icons/icon.icns',
    bundle_identifier=None,
    info_plist={'NSHighResolutionCapable': 'True'},
)