# -*- mode: python ; coding: utf-8 -*-
"""
SafeBrowser PyInstaller spec fayl
Build: pyinstaller safebrowser.spec --noconfirm --clean
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# ============================================
# Og'ir paketlarni to'liq yig'ish
# ============================================
torch_d, torch_b, torch_h = collect_all('torch')
ort_d, ort_b, ort_h = collect_all('onnxruntime')
face_d, face_b, face_h = collect_all('insightface')
yolo_d, yolo_b, yolo_h = collect_all('ultralytics')

# ============================================
# Data fayllar
# ============================================
datas = [
    ('config/config.ini', 'config'),
    ('resources', 'resources'),
    ('weights', 'weights'),
] + torch_d + ort_d + face_d + yolo_d

# ============================================
# Binary fayllar (DLL, SO)
# ============================================
binaries = torch_b + ort_b + face_b + yolo_b

# ============================================
# Hidden imports
# ============================================
hiddenimports = [
    # PyQt6 WebEngine
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebChannel',
    # Windows API
    'win32api', 'win32con', 'win32gui',
    'pywintypes', 'pythoncom',
    # CV / ML
    'cv2', 'numpy', 'PIL', 'sklearn', 'scipy',
    # System / Network
    'keyboard', 'mss', 'pyautogui', 'psutil', 'requests',
    # Encoding
    'encodings', 'encodings.utf_8',
] + torch_h + ort_h + face_h + yolo_h

# ===========================================
# Analysis
# ===========================================
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
    optimize=0,
)

# ============================================
# PYZ (Python bytecode archive)
# ============================================
pyz = PYZ(a.pure)

# ============================================
# EXE
# ============================================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SafeBrowser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    contents_directory='.',
)

# ============================================
# COLLECT (onedir)
# ============================================
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SafeBrowser',
)
