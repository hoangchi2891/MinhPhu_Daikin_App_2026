# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['H:/DAIKIN/MinhPhu_Daikin_App/app_desktop.py'],
    pathex=['H:/DAIKIN/MinhPhu_Daikin_App'],
    binaries=[],
    datas=[('H:/DAIKIN/MinhPhu_Daikin_App/web', 'web')],
    hiddenimports=['hvac_engine', 'hvac_report_exporter', 'ezdxf', 'win32com.client'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'tkinter', 'PyQt5', 'PySide6', 'pytest'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MinhPhu_Daikin_Quote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['H:/DAIKIN/MinhPhu_Daikin_App/web/assets/app_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MinhPhu_Daikin_Quote',
)
