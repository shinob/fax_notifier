# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = (
    collect_submodules("flask")
    + collect_submodules("jinja2")
    + collect_submodules("werkzeug")
    + collect_submodules("linebot")
    + collect_submodules("slack_sdk")
    + [
        "watchdog.observers.winapi",
        "watchdog.observers.polling",
        "watchdog.observers.read_directory_changes",
        "sqlite3",
        "PIL.Image",
    ]
)

a = Analysis(
    ["fax_notifier/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("fax_notifier/web/templates", "web/templates"),
        ("fax_notifier/web/static", "web/static"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="fax_notifier",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
