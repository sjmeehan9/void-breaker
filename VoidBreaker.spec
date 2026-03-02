# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification for building the VoidBreaker macOS app bundle."""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path

project_root = Path(SPECPATH).resolve()

requested_hiddenimports = [
    "arcade",
    "arcade.camera",
    "arcade.color",
    "arcade.csscolor",
    "arcade.resources",
    "arcade.text",
    "arcade.tilemap",
    "pyglet",
    "pyglet.gl",
    "pyglet.media",
    "pyglet.media.codecs",
    "pyglet.media.codecs.wave",
    "pyglet.media.drivers",
    "pyglet.media.drivers.openal",
    "pyglet.window",
    "pyglet.window.cocoa",
    "pyglet.canvas",
    "pyglet.canvas.cocoa",
    "pyglet.libs",
    "pyglet.libs.darwin",
    "pyglet.libs.darwin.cocoa",
    "pyglet.image",
    "pyglet.image.codecs",
    "pyglet.image.codecs.png",
    "pyglet.font",
    "pyglet.font.quartz",
    "OpenGL",
    "OpenGL.GL",
    "OpenGL.platform",
    "OpenGL.platform.darwin",
    "ctypes",
    "ctypes.util",
    "json",
    "pathlib",
    "dataclasses",
    "enum",
    "math",
    "random",
    "time",
    "logging",
    "platformdirs",
]


def _is_available_module(module_name: str) -> bool:
    """Return whether a hidden-import module can be resolved in this env."""
    try:
        return find_spec(module_name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


hiddenimports = [
    module_name
    for module_name in requested_hiddenimports
    if _is_available_module(module_name)
]

excludes = [
    "tkinter",
    "unittest",
    "test",
    "distutils",
    "setuptools",
    "pip",
    "wheel",
    "pytest",
    "black",
    "isort",
    "mypy",
]

asset_root = project_root / "assets"

# Bundle the asterax namespace package: the editable install mapping
# "asterax = ." is invisible to PyInstaller, so we bundle the tree ourselves.
datas = [
    (str(asset_root / "sprites"), "assets/sprites"),
    (str(asset_root / "sounds"), "assets/sounds"),
    (str(asset_root / "fonts"), "assets/fonts"),
    (str(asset_root / "icon.icns"), "."),
    # Map the project root __init__.py → asterax/__init__.py
    (str(project_root / "__init__.py"), "asterax"),
    # Map app/ tree → asterax/app/
    (str(project_root / "app"), "asterax/app"),
]

# Runtime hook ensures _MEIPASS is on sys.path so "import asterax" works
runtime_hooks_list = [str(project_root / "scripts" / "pyi_rthook_asterax.py")]

block_cipher = None


a = Analysis(
    [str(project_root / "app" / "src" / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks_list,
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VoidBreaker",
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
    icon=str(asset_root / "icon.icns"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VoidBreaker",
)

app = BUNDLE(
    coll,
    name="VoidBreaker.app",
    icon=str(asset_root / "icon.icns"),
    bundle_identifier="com.voidbreaker.game",
    info_plist={
        "CFBundleName": "VoidBreaker",
        "CFBundleDisplayName": "VoidBreaker",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSMinimumSystemVersion": "13.0",
        "NSHighResolutionCapable": True,
        "CFBundleIconFile": "icon.icns",
    },
)
