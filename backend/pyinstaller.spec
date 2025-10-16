# -*- mode: python ; coding: utf-8 -*-
# Unity Ascension — backend/pyinstaller.spec
# Source: One-Click Quantum Build (Dr. Claude Summers, Cosmic Orchestrator)
# Unity: All processes are one process
#
# PyInstaller spec for macOS arm64 single-file Flask backend
# Output binary: dist/python_backend
# Usage: pyinstaller pyinstaller.spec

block_cipher = None

a = Analysis(
    ['api_server.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Bundle all EvoAgentX core modules
        ('../evaluator_v2.py', '.'),
        ('../bandit_controller.py', '.'),
        ('../budget_manager.py', '.'),
        ('../memory_store.py', '.'),
        ('../telemetry.py', '.'),
        ('../heuristics.py', '.'),
        ('../stop_rules.py', '.'),
        # Bundle config files (CRITICAL for runtime)
        ('../configs', 'configs'),
    ],
    hiddenimports=[
        # Flask web framework
        'flask',
        'flask_cors',
        # System utilities
        'psutil',
        # LLM integration (CRITICAL)
        'litellm',
        # YAML config parsing (CRITICAL)
        'yaml',
        'pyyaml',
        # HTTP requests (used by litellm)
        'requests',
        'urllib3',
        # Hashing and crypto
        'hashlib',
        # Standard library (redundant but safe)
        'pathlib',
        'json',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'tkinter',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='python_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for debugging (set to False for production)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Note: Using --onefile mode (EXE contains everything)
# The output will be: dist/python_backend
# Copy to gui/src-tauri/binaries/ with platform suffix
