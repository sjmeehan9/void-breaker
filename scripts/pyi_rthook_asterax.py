"""PyInstaller runtime hook to resolve the asterax namespace package.

The project uses a setuptools editable-install mapping (asterax = ".") that
PyInstaller cannot follow during analysis.  We bundle the project source as
data files under an ``asterax/`` directory inside ``_MEIPASS`` and this hook
ensures the frozen ``sys.path`` includes ``_MEIPASS`` so that
``import asterax.app.src...`` resolves to those files.
"""

import os
import sys

# _MEIPASS is the temp directory where PyInstaller extracts bundled files.
meipass = getattr(sys, "_MEIPASS", None)
if meipass and meipass not in sys.path:
    sys.path.insert(0, meipass)

# Also ensure the asterax package directory itself is importable
if meipass:
    asterax_dir = os.path.join(meipass, "asterax")
    if os.path.isdir(asterax_dir) and asterax_dir not in sys.path:
        sys.path.insert(0, asterax_dir)
