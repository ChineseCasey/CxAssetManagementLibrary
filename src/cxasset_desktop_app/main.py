from __future__ import annotations

import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
except Exception:
    from PySide2.QtWidgets import QApplication

from cxasset_desktop_app.ui import DesktopWindow
from cxasset_desktop_app.dayu import setup_dayu_import_path


def _apply_dayu_theme(app: QApplication) -> None:
    setup_dayu_import_path()
    try:
        from dayu_widgets import dayu_theme  # type: ignore

        dayu_theme.apply(app)
    except Exception:
        pass


def run() -> int:
    app = QApplication(sys.argv)
    _apply_dayu_theme(app)
    w = DesktopWindow()
    w.show()
    if hasattr(app, "exec"):
        return app.exec()
    return app.exec_()


__all__ = ["run"]

