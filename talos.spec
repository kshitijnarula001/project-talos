# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['/Users/kshitij/Desktop/Talos'],
    binaries=[],
    datas=[
        ('core/*.py', 'core'),
        ('interface/*.py', 'interface'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'customtkinter',
        'ollama',
        'chromadb',
        'feedparser',
        'requests',
        'bs4',
        'duckduckgo_search',
        'whisper',
        'sounddevice',
        'scipy',
        'numpy',
        'fitz',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Talos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Talos',
)

app = BUNDLE(
    coll,
    name='Talos.app',
    icon=None,
    bundle_identifier='com.talos.ai',
    info_plist={
        'NSMicrophoneUsageDescription': 
            'Talos needs microphone access for voice input',
        'NSHighResolutionCapable': True,
    }
)