from __future__ import annotations

import builtins
import sys
from pathlib import Path


def setup_dayu_import_path() -> None:
    # dayu_widgets uses non-package absolute imports like `from theme import MTheme`.
    repo_root = Path(__file__).resolve().parents[2]
    dayu_root = repo_root / "third_party" / "dayu_widgets"
    dayu_pkg = dayu_root / "dayu_widgets"
    for p in (dayu_root, dayu_pkg):
        p_str = str(p)
        if p.exists() and p_str not in sys.path:
            sys.path.insert(0, p_str)

    # dayu_widgets has python2-era symbols.
    if not hasattr(builtins, "basestring"):
        builtins.basestring = str  # type: ignore[attr-defined]
    if not hasattr(builtins, "unicode"):
        builtins.unicode = str  # type: ignore[attr-defined]

