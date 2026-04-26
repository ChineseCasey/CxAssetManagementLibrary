from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from PySide6.QtCore import Qt, QSize, QPoint, QEvent
    from PySide6.QtGui import QPixmap, QIcon
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QListView,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QSizePolicy,
        QSlider,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QToolButton,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except Exception:
    from PySide2.QtCore import Qt, QSize, QPoint, QEvent
    from PySide2.QtGui import QPixmap, QIcon
    from PySide2.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QListView,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QSizePolicy,
        QSlider,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QToolButton,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

from cxasset_desktop_app.client import ApiClient
from cxasset_desktop_app.dayu import setup_dayu_import_path

setup_dayu_import_path()

DAYU_ENABLED = False
try:
    from dayu_widgets import MCard, MComboBox, MLabel, MLineEdit, MPushButton  # type: ignore

    DAYU_ENABLED = True
except Exception:
    MCard = QFrame  # type: ignore
    MComboBox = QComboBox  # type: ignore
    MLabel = QLabel  # type: ignore
    MLineEdit = QLabel  # type: ignore
    MPushButton = QLabel  # type: ignore


def make_line_edit(placeholder: str, text: str = ""):
    if DAYU_ENABLED:
        w = MLineEdit(text)
        w.setPlaceholderText(placeholder)
        try:
            w.medium()
        except Exception:
            pass
        return w
    try:
        from PySide6.QtWidgets import QLineEdit as _QLineEdit  # type: ignore
    except Exception:
        from PySide2.QtWidgets import QLineEdit as _QLineEdit  # type: ignore
    w = _QLineEdit(text)
    w.setPlaceholderText(placeholder)
    return w


def make_button(text: str, primary: bool = False):
    if DAYU_ENABLED:
        w = MPushButton(text)
        if primary:
            try:
                w.primary()
            except Exception:
                pass
        return w
    try:
        from PySide6.QtWidgets import QPushButton as _QPushButton  # type: ignore
    except Exception:
        from PySide2.QtWidgets import QPushButton as _QPushButton  # type: ignore
    return _QPushButton(text)


class ScaledPreviewLabel(QLabel):
    """Keeps aspect ratio while using the available width/height from the splitter."""

    def __init__(self) -> None:
        super().__init__()
        self._source: QPixmap | None = None
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_preview_pixmap(self, px: QPixmap | None) -> None:
        if px is None or px.isNull():
            self._source = None
            self.clear()
            self.setText("无预览")
            return
        self.setText("")
        self._source = QPixmap(px)
        self._apply()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply()

    def _apply(self) -> None:
        if self._source is None or self._source.isNull():
            return
        m = self.contentsMargins()
        w = max(32, self.width() - m.left() - m.right())
        h = max(32, self.height() - m.top() - m.bottom())
        scaled = self._source.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().setPixmap(scaled)


class AssetCardWidget(QWidget):
    def __init__(
        self,
        title: str,
        subtitle: str,
        pixmap: QPixmap | None,
        favored: bool,
        thumb_w: int,
        thumb_h: int,
        on_star_clicked,
    ) -> None:
        super().__init__()
        self._title = QLabel(title)
        self._subtitle = QLabel(subtitle)
        self._thumb = QLabel()
        self._star = QToolButton()
        self._star.setText("★" if favored else "☆")
        self._star.setObjectName("cardStar")
        self._star.setAutoRaise(True)
        self._star.setCursor(Qt.PointingHandCursor)
        self._star.clicked.connect(on_star_clicked)
        self._thumb_w = thumb_w
        self._thumb_h = thumb_h
        self._thumb.setFixedSize(thumb_w, thumb_h)
        self._thumb.setAlignment(Qt.AlignCenter)
        if pixmap and not pixmap.isNull():
            self._thumb.setPixmap(
                pixmap.scaled(thumb_w, thumb_h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )
        else:
            self._thumb.setText("无缩略图")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(self._star)
        layout.addLayout(top)
        layout.addWidget(self._thumb)
        layout.addWidget(self._title)
        layout.addWidget(self._subtitle)
        self.setObjectName("assetCard")

    def set_favorite(self, favored: bool) -> None:
        self._star.setText("★" if favored else "☆")


class ManageDialog(QDialog):
    def __init__(self, win: "DesktopWindow") -> None:
        super().__init__(win)
        self.win = win
        self.setWindowTitle("目录与资产管理")
        self.resize(1120, 760)
        self.setObjectName("manageDialog")

        lay = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.setObjectName("manageTabs")
        lay.addWidget(tabs)
        tabs.addTab(self._build_create_tab(), "创建")
        tabs.addTab(self._build_delete_tab(), "删除")

    def _module_options(self):
        return self.win.modules

    def _fill_combo(self, combo, rows, text_key="name", data_key="id"):
        combo.clear()
        for r in rows:
            combo.addItem(str(r[text_key]), r[data_key])

    def _nodes_for_module(self, module_id: int):
        return self.win.get_nodes_for_module(module_id)

    @staticmethod
    def _make_card(title: str, subtitle: str | None = None) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("manageCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 14)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignTop)
        t = QLabel(title)
        t.setObjectName("manageCardTitle")
        lay.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("manageCardSubTitle")
            lay.addWidget(s)
        return card, lay

    def _build_create_tab(self):
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)
        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(12)
        top_grid.setVerticalSpacing(12)
        lay.addLayout(top_grid)
        bottom_grid = QGridLayout()
        lay.addLayout(bottom_grid)

        self.create_module_name = make_line_edit("模块名，如 Lighting")
        self.create_module_btn = make_button("新增模块", primary=True)
        self.create_module_btn.clicked.connect(self.create_module)
        card1, card1_lay = self._make_card("1) 新增模块")
        c1f = QFormLayout()
        c1f.addRow("模块名", self.create_module_name)
        c1f.addRow("", self.create_module_btn)
        card1_lay.addLayout(c1f)
        top_grid.addWidget(card1, 0, 0)

        self.create_type_module_combo = QComboBox()
        self._fill_combo(self.create_type_module_combo, self._module_options())
        self.create_type_name = make_line_edit("类型目录名，如 HDRI")
        self.create_type_btn = make_button("新增类型目录", primary=True)
        self.create_type_btn.clicked.connect(self.create_type)
        card2, card2_lay = self._make_card("2) 新增类型目录")
        c2f = QFormLayout()
        c2f.addRow("属于哪个模块", self.create_type_module_combo)
        c2f.addRow("类型目录名", self.create_type_name)
        c2f.addRow("", self.create_type_btn)
        card2_lay.addLayout(c2f)
        top_grid.addWidget(card2, 0, 1)

        self.create_asset_module_combo = QComboBox()
        self._fill_combo(self.create_asset_module_combo, self._module_options())
        self.create_asset_node_combo = QComboBox()
        self.create_asset_module_combo.currentIndexChanged.connect(self.refresh_asset_nodes)
        self.create_asset_name = make_line_edit("资产名，如 Micah_Loft")
        self.create_subdir_name = make_line_edit("先创建子目录(可选)")
        self.thumb_path_label = QLabel("(未选择)")
        self.asset_path_label = QLabel("(未选择)")
        self.thumb_path = None
        self.asset_path = None
        thumb_btn = make_button("选择缩略图")
        file_btn = make_button("选择资产文件")
        thumb_btn.clicked.connect(self.select_thumb)
        file_btn.clicked.connect(self.select_asset_file)
        self.create_asset_btn = make_button("新增资产", primary=True)
        self.create_asset_btn.clicked.connect(self.create_asset)
        card3, card3_lay = self._make_card("3) 上传资产到目标目录")
        c3f = QFormLayout()
        c3f.addRow("模块", self.create_asset_module_combo)
        c3f.addRow("归属目录（类型或子类型）", self.create_asset_node_combo)
        c3f.addRow("先创建子目录（可选）", self.create_subdir_name)
        c3f.addRow("资产名称", self.create_asset_name)
        row1 = QHBoxLayout(); row1.addWidget(thumb_btn); row1.addWidget(self.thumb_path_label)
        c3f.addRow("缩略图（jpg/png）", row1)
        row2 = QHBoxLayout(); row2.addWidget(file_btn); row2.addWidget(self.asset_path_label)
        c3f.addRow("原始资产文件（例如 .exr）", row2)
        c3f.addRow("", self.create_asset_btn)
        card3_lay.addLayout(c3f)
        bottom_grid.addWidget(card3, 0, 0, 1, 2)
        self.refresh_asset_nodes()
        return wrap

    def _build_delete_tab(self):
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        lay.addLayout(grid)

        self.delete_node_module_combo = QComboBox()
        self._fill_combo(self.delete_node_module_combo, self._module_options())
        self.delete_node_combo = QComboBox()
        self.delete_node_module_combo.currentIndexChanged.connect(self.refresh_delete_nodes)
        self.delete_node_btn = make_button("删除目录（含子层级）")
        self.delete_node_btn.setObjectName("dangerBtn")
        self.delete_node_btn.clicked.connect(self.delete_node)
        card1, card1_lay = self._make_card("删除目录")
        d1l = QVBoxLayout()
        d1l.setSpacing(8)
        d1l.addWidget(QLabel("模块"))
        d1l.addWidget(self.delete_node_module_combo)
        d1l.addWidget(QLabel("选择要删除的目录"))
        d1l.addWidget(self.delete_node_combo)
        d1l.addWidget(self.delete_node_btn)
        card1_lay.addLayout(d1l)
        grid.addWidget(card1, 0, 0)

        self.delete_asset_module_combo = QComboBox()
        self._fill_combo(self.delete_asset_module_combo, self._module_options())
        self.delete_asset_path_combo = QComboBox()
        self.delete_asset_path_combo.currentIndexChanged.connect(self.refresh_delete_assets)
        self.delete_asset_module_combo.currentIndexChanged.connect(self.refresh_delete_asset_paths)
        self.delete_asset_combo = QComboBox()
        self.delete_asset_module_combo.currentIndexChanged.connect(self.refresh_delete_assets)
        self.delete_asset_btn = make_button("删除资产")
        self.delete_asset_btn.setObjectName("dangerBtn")
        self.delete_asset_btn.clicked.connect(self.delete_asset)
        card2, card2_lay = self._make_card("删除资产")
        d2l = QVBoxLayout()
        d2l.setSpacing(8)
        d2l.addWidget(QLabel("模块"))
        d2l.addWidget(self.delete_asset_module_combo)
        d2l.addWidget(QLabel("资产所在目录（可选）"))
        d2l.addWidget(self.delete_asset_path_combo)
        d2l.addWidget(QLabel("选择要删除的资产"))
        d2l.addWidget(self.delete_asset_combo)
        d2l.addWidget(self.delete_asset_btn)
        card2_lay.addLayout(d2l)
        grid.addWidget(card2, 0, 1)
        lay.addStretch(1)
        self.refresh_delete_nodes()
        self.refresh_delete_asset_paths()
        self.refresh_delete_assets()
        return wrap

    def refresh_asset_nodes(self):
        module_id = self.create_asset_module_combo.currentData()
        if module_id is None:
            self.create_asset_node_combo.clear()
            return
        nodes = self._nodes_for_module(int(module_id))
        self.create_asset_node_combo.clear()
        for n in nodes:
            self.create_asset_node_combo.addItem(n["path"], n["id"])

    def refresh_delete_nodes(self):
        module_id = self.delete_node_module_combo.currentData()
        if module_id is None:
            self.delete_node_combo.clear()
            return
        module_id = int(module_id)
        nodes = self._nodes_for_module(module_id)
        self.delete_node_combo.clear()
        module_name = ""
        module_path = ""
        for m in self.win.modules:
            if int(m.get("id", -1)) == module_id:
                module_name = str(m.get("name") or "")
                module_path = str(m.get("path") or module_name)
                break
        # Allow deleting module root (and its full subtree), as requested.
        self.delete_node_combo.addItem(f"[模块] {module_name or module_path}", module_id)
        for n in nodes:
            self.delete_node_combo.addItem(n["path"], n["id"])

    def refresh_delete_assets(self):
        module_id = self.delete_asset_module_combo.currentData()
        self.delete_asset_combo.clear()
        if module_id is None:
            return
        prefix = ""
        for m in self.win.modules:
            if int(m["id"]) == int(module_id):
                prefix = m["path"] + "/"
                break
        path_filter = self.delete_asset_path_combo.currentText().strip()
        for a in self.win.all_assets:
            node_path = a.get("node_path") or ""
            if node_path == prefix[:-1] or node_path.startswith(prefix):
                if path_filter and path_filter != "全部" and not (node_path == path_filter or node_path.startswith(path_filter + "/")):
                    continue
                label = f"{node_path} / {a.get('name')}"
                self.delete_asset_combo.addItem(label, a["id"])

    def refresh_delete_asset_paths(self):
        module_id = self.delete_asset_module_combo.currentData()
        self.delete_asset_path_combo.clear()
        self.delete_asset_path_combo.addItem("全部")
        if module_id is None:
            return
        nodes = self._nodes_for_module(int(module_id))
        for n in nodes:
            self.delete_asset_path_combo.addItem(n["path"])

    def create_module(self):
        name = self.create_module_name.text().strip()
        if not name:
            return
        self.win.client.create_node(self.win.library_id, None, name)
        self.win.reload_all()
        self.close()

    def create_type(self):
        module_id = self.create_type_module_combo.currentData()
        name = self.create_type_name.text().strip()
        if module_id is None or not name:
            return
        self.win.client.create_node(self.win.library_id, int(module_id), name)
        self.win.reload_all()
        self.close()

    def select_thumb(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择缩略图")
        if path:
            self.thumb_path = path
            self.thumb_path_label.setText(path)

    def select_asset_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择资产文件")
        if path:
            self.asset_path = path
            self.asset_path_label.setText(path)

    def create_asset(self):
        node_id = self.create_asset_node_combo.currentData()
        name = self.create_asset_name.text().strip()
        subdir = self.create_subdir_name.text().strip()
        if node_id is None or not name:
            return
        target_node = int(node_id)
        if subdir:
            node = self.win.client.create_node(self.win.library_id, target_node, subdir)
            target_node = int(node["id"])
        self.win.client.create_asset(
            library_id=self.win.library_id,
            node_id=target_node,
            name=name,
            thumbnail_path=self.thumb_path,
            asset_file_path=self.asset_path,
        )
        self.win.reload_all()
        self.close()

    def delete_node(self):
        node_id = self.delete_node_combo.currentData()
        if node_id is None:
            return
        self.win.client.delete_node(int(node_id))
        self.win.reload_all()
        self.close()

    def delete_asset(self):
        asset_id = self.delete_asset_combo.currentData()
        if asset_id is None:
            return
        self.win.client.delete_asset(int(asset_id))
        self.win.reload_all()
        self.close()


class DesktopWindow(QMainWindow):
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        super().__init__()
        self.client = ApiClient(base_url=base_url)
        self.library_id: int | None = None
        self.modules: list[dict[str, Any]] = []
        self.assets: list[dict[str, Any]] = []
        self.all_assets: list[dict[str, Any]] = []
        self.module_nodes: dict[int, list[dict[str, Any]]] = {}
        self.favorites: set[int] = set()
        self.thumb_cache: dict[str, QPixmap] = {}
        self._card_thumb_w: int = 210
        self._theme_dark: bool = True
        self.view_mode: str = "card"
        self._drag_pos: QPoint | None = None
        self._resize_margin: int = 6
        self._resizing: bool = False
        self._resize_edges: tuple[bool, bool, bool, bool] = (False, False, False, False)  # left, right, top, bottom
        self._resize_start_pos: QPoint | None = None
        self._resize_start_geo = None
        self._is_topmost = False
        self._icon_root = Path(__file__).resolve().parents[3] / "CXA_Icon" / "button"
        self._app_title_icon = Path(__file__).resolve().parents[3] / "CXA_Icon" / "title_icon.png"
        self.setWindowTitle("CxAsset Desktop")
        self.resize(1700, 980)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        if self._app_title_icon.exists():
            wico = QIcon(str(self._app_title_icon))
            if not wico.isNull():
                self.setWindowIcon(wico)
        self._build_ui()
        self._install_resize_event_filters(self)
        self._apply_theme_style()
        self.reload_all()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("rootWidget")
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(8, 6, 8, 6)
        top_layout.setSpacing(6)
        top_bar.mousePressEvent = self._title_mouse_press
        top_bar.mouseMoveEvent = self._title_mouse_move
        top_bar.mouseReleaseEvent = self._title_mouse_release
        top_bar.mouseDoubleClickEvent = lambda _e: self.toggle_max_restore()

        self.logo = QWidget()
        logo_lay = QHBoxLayout(self.logo)
        logo_lay.setContentsMargins(0, 0, 0, 0)
        logo_lay.setSpacing(8)
        self.logo_img = QLabel()
        self.logo_img.setFixedSize(28, 28)
        if self._app_title_icon.exists():
            lp = QPixmap(str(self._app_title_icon))
            if not lp.isNull():
                self.logo_img.setPixmap(lp.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_text = QLabel("CxAsset")
        self.logo_text.setObjectName("logoText")
        logo_lay.addWidget(self.logo_img)
        logo_lay.addWidget(self.logo_text)

        self.search_edit = make_line_edit("搜索资产名称...")
        self.search_edit.setObjectName("searchEdit")
        self.search_edit.textChanged.connect(self.render_assets)
        self.token_edit = make_line_edit("media token", "dev-token")
        self.token_edit.setObjectName("tokenEdit")
        self.token_edit.editingFinished.connect(self.sync_token)
        self.view_toggle_btn = make_button("列表")
        self.view_toggle_btn.setObjectName("neutralBtn")
        self.view_toggle_btn.clicked.connect(self.toggle_view_mode)
        self.fav_only_btn = make_button("仅看收藏(0)")
        self.fav_only_btn.setObjectName("neutralBtn")
        try:
            self.fav_only_btn.setCheckable(True)
            self.fav_only_btn.toggled.connect(lambda _v: self.render_assets())
        except Exception:
            pass
        self.manage_btn = make_button("管理面板")
        self.manage_btn.setObjectName("neutralBtn")
        self.manage_btn.clicked.connect(self.open_manage_dialog)
        self.refresh_btn = make_button("刷新", primary=True)
        self.refresh_btn.setObjectName("neutralBtn")
        self.refresh_btn.clicked.connect(self.reload_all)
        self.theme_label = QLabel("Dark")
        self.theme_label.setObjectName("themeLabel")
        self.theme_toggle = QCheckBox()
        self.theme_toggle.setObjectName("themeToggle")
        self.theme_toggle.setChecked(True)
        self.theme_toggle.toggled.connect(self.toggle_theme)
        self.pin_btn = self._title_win_button("zhiding.png", "置顶", self.toggle_topmost)
        self.min_btn = self._title_win_button("min.png", "最小化", self.showMinimized)
        self.max_btn = self._title_win_button("max.png", "全屏", self.toggle_fullscreen)
        self.close_btn = self._title_win_button("close.png", "关闭", self.close)

        top_layout.addWidget(self.logo)
        top_layout.addStretch()
        top_layout.addWidget(self.search_edit)
        top_layout.addWidget(self.token_edit)
        top_layout.addWidget(self.view_toggle_btn)
        top_layout.addWidget(self.fav_only_btn)
        top_layout.addWidget(self.manage_btn)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.theme_label)
        top_layout.addWidget(self.theme_toggle)
        top_layout.addWidget(self.pin_btn)
        top_layout.addWidget(self.min_btn)
        top_layout.addWidget(self.max_btn)
        top_layout.addWidget(self.close_btn)
        root_layout.addWidget(top_bar)

        self.body_splitter = QSplitter(Qt.Horizontal)
        body = self.body_splitter
        root_layout.addWidget(body, 1)

        left = QFrame(); left.setObjectName("panel")
        ll = QVBoxLayout(left); ll.addWidget(QLabel("模块"))
        ll.setContentsMargins(6, 6, 6, 6)
        ll.setSpacing(4)
        self.module_combo = QComboBox()
        self.module_combo.setObjectName("moduleCombo")
        self.module_combo.currentIndexChanged.connect(self.on_module_changed)
        ll.addWidget(self.module_combo)
        self.tree = QTreeWidget()
        self.tree.setObjectName("navTree")
        self.tree.setHeaderLabels(["目录"])
        self.tree.currentItemChanged.connect(self._on_tree_current_changed)
        ll.addWidget(self.tree, 1)
        body.addWidget(left)

        center = QFrame()
        center.setObjectName("panel")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(6, 6, 6, 6)
        cl.setSpacing(4)
        top_row = QHBoxLayout()
        self.breadcrumb = QLabel("当前路径: -")
        top_row.addWidget(self.breadcrumb, 1)
        self.thumb_slider_label = QLabel("卡片大小")
        self.thumb_size_slider = QSlider(Qt.Horizontal)
        self.thumb_size_slider.setRange(120, 280)
        self.thumb_size_slider.setValue(210)
        self.thumb_size_slider.setFixedWidth(160)
        self.thumb_size_slider.valueChanged.connect(self._on_thumb_slider_changed)
        top_row.addWidget(self.thumb_slider_label)
        top_row.addWidget(self.thumb_size_slider)
        cl.addLayout(top_row)
        self.asset_list = QListWidget()
        self.asset_list.setObjectName("assetList")
        self.asset_list.setViewMode(QListWidget.IconMode)
        self.asset_list.setResizeMode(QListWidget.Adjust)
        self.asset_list.setIconSize(QSize(210, 118))
        self.asset_list.setGridSize(QSize(240, 184))
        self.asset_list.itemClicked.connect(self.on_asset_clicked)
        self.asset_list.itemDoubleClicked.connect(self.on_asset_double_clicked)
        cl.addWidget(self.asset_list, 1)
        body.addWidget(center)

        right = QFrame()
        right.setObjectName("panel")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(6, 6, 6, 6)
        rl.setSpacing(6)
        rl.addWidget(QLabel("资产详情"))
        self.preview = ScaledPreviewLabel()
        form = QFormLayout()
        self.detail_name = QLabel("—")
        self.detail_type = QLabel("—")
        self.detail_file_type = QLabel("—")
        self.detail_file_size = QLabel("—")
        self.detail_set_date = QLabel("—")
        self.detail_status = QLabel("—")
        self.detail_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detail_type.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detail_file_type.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detail_file_size.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detail_set_date.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detail_status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("Name", self.detail_name)
        form.addRow("Type", self.detail_type)
        form.addRow("FileType", self.detail_file_type)
        form.addRow("FileSize", self.detail_file_size)
        form.addRow("setDate", self.detail_set_date)
        form.addRow("Status", self.detail_status)
        self.detail_files_label = QLabel("文件")
        self.detail_text = QTextEdit()
        self.detail_text.setObjectName("detailText")
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(220)
        rl.addWidget(self.preview, 1)
        rl.addLayout(form)
        rl.addWidget(self.detail_files_label)
        rl.addWidget(self.detail_text, 0)
        body.addWidget(right)
        body.setSizes([320, 940, 430])
        body.setHandleWidth(2)

    def _title_win_button(self, icon_name: str, tip: str, slot) -> QToolButton:
        target = QToolButton(self)
        icon_path = self._icon_root / icon_name
        if icon_path.exists():
            target.setIcon(QIcon(str(icon_path)))
        else:
            target.setText(tip[0] if tip else "?")
        target.setToolTip(tip)
        target.setIconSize(QSize(16, 16))
        target.setFixedSize(32, 28)
        target.setObjectName("winCtrlBtn")
        target.setAutoRaise(True)
        target.setCursor(Qt.PointingHandCursor)
        target.clicked.connect(slot)
        return target

    def _on_thumb_slider_changed(self, v: int) -> None:
        self._card_thumb_w = int(v)
        self.render_assets()

    def _on_tree_current_changed(self, current: QTreeWidgetItem | None, _previous) -> None:
        if current is not None:
            self.on_tree_clicked(current)

    def _apply_theme_style(self) -> None:
        if self._theme_dark:
            style = """
            QMainWindow, QWidget { background: #1e1f22; color: #d4d4d4; }
            QWidget#rootWidget { background: #1e1f22; }
            QDialog#manageDialog { background: #252526; color: #d4d4d4; }
            QFrame#topBar { background: #252526; border: 0; border-bottom: 1px solid #31343b; border-radius: 0; }
            #logoText { font-weight: 600; font-size: 15px; color: #d7dae0; }
            QFrame#panel, QFrame#manageCard { background: #202124; border: 1px solid #31343b; border-radius: 8px; }
            QLabel#manageCardTitle { font-size: 15px; font-weight: 600; color: #e2e6ee; }
            QLabel#manageCardSubTitle { color: #a3aab8; }
            QTreeWidget, QListWidget, QTextEdit, QComboBox, QLineEdit, QTabWidget::pane {
                background: #181a1f; border: 1px solid #31343b; border-radius: 6px;
            }
            QTreeWidget::viewport, QListWidget::viewport, QTextEdit::viewport {
                background: #181a1f;
            }
            QTreeWidget::item, QListWidget::item { background: transparent; color: #d4d4d4; }
            QTreeWidget::item:selected, QListWidget::item:selected { background: #2b2f36; color: #e5e7eb; }
            QTreeWidget::branch:selected { background: #2b2f36; }
            QSlider::groove:horizontal { background: #2f333a; height: 4px; border-radius: 2px; }
            QSlider::handle:horizontal { background: #8a94a7; width: 12px; margin: -4px 0; border-radius: 6px; border: 1px solid #636b79; }
            QComboBox::drop-down { border: none; width: 20px; }
            QLineEdit:focus, QTextEdit:focus, QTreeWidget:focus, QListWidget:focus, QComboBox:focus {
                border: 1px solid #3b82f6;
            }
            QTabBar::tab { background: transparent; border: none; padding: 6px 12px; color: #9ca3af; }
            QTabBar::tab:selected { color: #58a6ff; border-bottom: 2px solid #58a6ff; }
            QWidget#assetCard { background: #23262d; border: 1px solid #3a3f49; border-radius: 10px; }
            QToolButton#cardStar { border: none; background: transparent; color: #f6c453; }
            QSplitter::handle { background: #31343b; width: 2px; }
            QToolButton#winCtrlBtn { background: transparent; border: none; border-radius: 4px; padding: 2px; color: #d4d4d4; }
            QToolButton#winCtrlBtn:hover { background: #31343b; }
            QLabel#themeLabel { color: #c8ced8; font-size: 13px; }
            QPushButton, QToolButton, MPushButton {
                background: #2b2f36;
                border: 1px solid #3a3f49;
                border-radius: 6px;
                padding: 5px 10px;
                color: #dce2ea;
            }
            QPushButton:hover, QToolButton:hover, MPushButton:hover { background: #343943; border-color: #4a515f; }
            QPushButton:pressed, QToolButton:pressed, MPushButton:pressed { background: #2a2f38; }
            QPushButton#dangerBtn, MPushButton#dangerBtn {
                background: transparent;
                border: 1px solid #a33a44;
                color: #e16575;
            }
            QPushButton#dangerBtn:hover, MPushButton#dangerBtn:hover {
                background: rgba(163, 58, 68, 0.12);
                border-color: #c2525f;
            }
            QScrollBar:vertical, QScrollBar:horizontal { background: #1e1f22; border: none; }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #3b404a;
                border-radius: 4px;
                min-height: 24px;
                min-width: 24px;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #4a515f; }
            QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; border: none; background: transparent; }
            QCheckBox#themeToggle {
                spacing: 0px;
                min-width: 46px;
                max-width: 46px;
                min-height: 24px;
                max-height: 24px;
            }
            QCheckBox#themeToggle::indicator {
                width: 46px;
                height: 24px;
                border-radius: 12px;
                background: #3a3f49;
                border: 1px solid #505765;
            }
            QCheckBox#themeToggle::indicator:checked {
                background: #3b82f6;
                border: 1px solid #5fa1ff;
            }
            """
            self.theme_label.setText("Dark")
        else:
            style = """
            QMainWindow, QWidget { background: #f3f5f8; color: #14181f; }
            QDialog#manageDialog { background: #f7f8fa; color: #171a22; }
            QFrame#topBar { background: #ffffff; border: 0; border-bottom: 1px solid #d6dde8; border-radius: 0; }
            #logoText { font-weight: 600; font-size: 15px; color: #1d2838; }
            QFrame#panel, QFrame#manageCard { background: #ffffff; border: 1px solid #d6dde8; border-radius: 8px; }
            QLabel#manageCardTitle { font-size: 15px; font-weight: 600; color: #1d2838; }
            QLabel#manageCardSubTitle { color: #5f6f84; }
            QTreeWidget, QListWidget, QTextEdit, QComboBox, QLineEdit, QTabWidget::pane {
                background: #ffffff; border: 1px solid #d6dde8; border-radius: 6px;
            }
            QTabBar::tab { background: transparent; border: none; padding: 6px 12px; color: #5f6f84; }
            QTabBar::tab:selected { color: #1677ff; border-bottom: 2px solid #1677ff; }
            QWidget#assetCard { background: #ffffff; border: 1px solid #d6dde8; border-radius: 10px; }
            QToolButton#cardStar { border: none; background: transparent; color: #d48a00; }
            QSplitter::handle { background: #d6dde8; width: 2px; }
            QToolButton#winCtrlBtn { background: transparent; border: none; border-radius: 4px; padding: 2px; }
            QToolButton#winCtrlBtn:hover { background: #edf2fa; }
            QPushButton#dangerBtn {
                background: transparent;
                border: 1px solid #d64550;
                color: #c9303f;
            }
            QPushButton#dangerBtn:hover {
                background: rgba(214, 69, 80, 0.08);
                border-color: #de5d67;
            }
            QLabel#themeLabel { color: #27364a; font-size: 13px; }
            QCheckBox#themeToggle {
                spacing: 0px;
                min-width: 46px;
                max-width: 46px;
                min-height: 24px;
                max-height: 24px;
            }
            QCheckBox#themeToggle::indicator {
                width: 46px;
                height: 24px;
                border-radius: 12px;
                background: #d2dae6;
                border: 1px solid #b8c4d5;
            }
            QCheckBox#themeToggle::indicator:checked {
                background: #1677ff;
                border: 1px solid #3e8fff;
            }
            """
            self.theme_label.setText("Light")
        self.setStyleSheet(style)
        self._apply_widget_palette_overrides()

    def _apply_widget_palette_overrides(self) -> None:
        if self._theme_dark:
            input_qss = "background:#181a1f;color:#d4d4d4;border:1px solid #31343b;border-radius:6px;padding:3px 6px;"
            neutral_btn_qss = "background:#2b2f36;color:#dce2ea;border:1px solid #3a3f49;border-radius:6px;padding:4px 10px;"
        else:
            input_qss = "background:#ffffff;color:#14181f;border:1px solid #d6dde8;border-radius:6px;padding:3px 6px;"
            neutral_btn_qss = "background:#ffffff;color:#1d2838;border:1px solid #d6dde8;border-radius:6px;padding:4px 10px;"

        for w in [
            self.search_edit,
            self.token_edit,
            self.module_combo,
            self.create_type_module_combo if hasattr(self, "create_type_module_combo") else None,
        ]:
            if w is not None:
                try:
                    w.setStyleSheet(input_qss)
                except Exception:
                    pass
        for w in [self.view_toggle_btn, self.fav_only_btn, self.manage_btn, self.refresh_btn]:
            try:
                w.setStyleSheet(neutral_btn_qss)
            except Exception:
                pass
        for w in [self.tree, self.asset_list, self.detail_text]:
            try:
                w.setStyleSheet(input_qss)
            except Exception:
                pass

    def toggle_theme(self, checked: bool) -> None:
        self._theme_dark = bool(checked)
        self._apply_theme_style()

    def _install_resize_event_filters(self, widget: QWidget) -> None:
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    def _edge_hit_test(self, global_pos: QPoint) -> tuple[bool, bool, bool, bool]:
        if self.isMaximized() or self.isFullScreen():
            return (False, False, False, False)
        g = self.frameGeometry()
        left = abs(global_pos.x() - g.left()) <= self._resize_margin
        right = abs(global_pos.x() - g.right()) <= self._resize_margin
        top = abs(global_pos.y() - g.top()) <= self._resize_margin
        bottom = abs(global_pos.y() - g.bottom()) <= self._resize_margin
        return (left, right, top, bottom)

    def _update_resize_cursor(self, edges: tuple[bool, bool, bool, bool]) -> None:
        left, right, top, bottom = edges
        if (left and top) or (right and bottom):
            self.setCursor(Qt.SizeFDiagCursor)
        elif (right and top) or (left and bottom):
            self.setCursor(Qt.SizeBDiagCursor)
        elif left or right:
            self.setCursor(Qt.SizeHorCursor)
        elif top or bottom:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.unsetCursor()

    def _perform_resize(self, global_pos: QPoint) -> None:
        if not self._resizing or self._resize_start_geo is None or self._resize_start_pos is None:
            return
        left, right, top, bottom = self._resize_edges
        dx = global_pos.x() - self._resize_start_pos.x()
        dy = global_pos.y() - self._resize_start_pos.y()
        g = self._resize_start_geo
        min_w = max(self.minimumWidth(), 720)
        min_h = max(self.minimumHeight(), 480)

        new_left = g.left()
        new_right = g.right()
        new_top = g.top()
        new_bottom = g.bottom()
        if left:
            new_left = min(g.left() + dx, new_right - min_w)
        if right:
            new_right = max(g.right() + dx, new_left + min_w)
        if top:
            new_top = min(g.top() + dy, new_bottom - min_h)
        if bottom:
            new_bottom = max(g.bottom() + dy, new_top + min_h)
        self.setGeometry(new_left, new_top, new_right - new_left + 1, new_bottom - new_top + 1)

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        et = event.type()
        if et == QEvent.MouseMove:
            gp = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            if self._resizing:
                self._perform_resize(gp)
                return True
            edges = self._edge_hit_test(gp)
            self._update_resize_cursor(edges)
        elif et == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            gp = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            edges = self._edge_hit_test(gp)
            if any(edges):
                self._resizing = True
                self._resize_edges = edges
                self._resize_start_pos = gp
                self._resize_start_geo = self.geometry()
                return True
        elif et == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self._resizing:
                self._resizing = False
                self._resize_edges = (False, False, False, False)
                self._resize_start_pos = None
                self._resize_start_geo = None
                self.unsetCursor()
                return True
        return super().eventFilter(watched, event)

    def _title_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft() if hasattr(event, "globalPosition") else event.globalPos() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton and not self.isMaximized():
            g = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            self.move(g - self._drag_pos)

    def _title_mouse_release(self, _event):
        self._drag_pos = None

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.max_btn.setToolTip("全屏")
        else:
            self.showFullScreen()
            self.max_btn.setToolTip("退出全屏")

    def toggle_topmost(self):
        self._is_topmost = not self._is_topmost
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self._is_topmost)
        self.show()
        self.pin_btn.setToolTip("取消置顶" if self._is_topmost else "置顶")

    def toggle_view_mode(self):
        self.view_mode = "list" if self.view_mode == "card" else "card"
        self.view_toggle_btn.setText("卡片" if self.view_mode == "list" else "列表")
        self.render_assets()

    def sync_token(self) -> None:
        self.client.set_media_token(self.token_edit.text())

    def get_nodes_for_module(self, module_id: int) -> list[dict[str, Any]]:
        if module_id in self.module_nodes:
            return self.module_nodes[module_id]
        if self.library_id is None:
            return []
        out = []
        def walk(parent_id: int):
            for n in self.client.get_tree(self.library_id, parent_id=parent_id):
                out.append(n)
                walk(int(n["id"]))
        walk(module_id)
        self.module_nodes[module_id] = out
        return out

    def load_all_assets(self):
        if self.library_id is None:
            return []
        page = 1
        all_items = []
        while True:
            data = self.client.request("GET", f"/libraries/{self.library_id}/assets?page={page}&page_size=200")
            items = data.get("items", [])
            all_items.extend(items)
            meta = data.get("meta", {})
            if not meta or page >= meta.get("total_pages", 1):
                break
            page += 1
        return all_items

    @staticmethod
    def _format_bytes(size: int | None) -> str:
        if size is None:
            return "-"
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def reload_all(self) -> None:
        try:
            libs = self.client.get_libraries()
            if not libs:
                QMessageBox.warning(self, "提示", "未找到库，请先运行同步。")
                return
            self.library_id = int(libs[0]["id"])
            self.modules = self.client.get_tree(self.library_id)
            self.module_nodes = {}
            self.all_assets = self.load_all_assets()
            try:
                self.favorites = set(self.client.get_favorite_ids(self.library_id))
            except Exception:
                self.favorites = set()
            self.module_combo.blockSignals(True)
            self.module_combo.clear()
            for m in self.modules:
                self.module_combo.addItem(m["name"], m)
            self.module_combo.blockSignals(False)
            if self.modules:
                self.module_combo.setCurrentIndex(0)
                self.on_module_changed(0)
        except Exception as exc:
            QMessageBox.critical(self, "加载失败", str(exc))

    def on_module_changed(self, index: int) -> None:
        if index < 0:
            return
        module = self.module_combo.itemData(index)
        if not module:
            return
        self.tree.clear()
        root = QTreeWidgetItem([module["name"]]); root.setData(0, Qt.UserRole, module)
        self.tree.addTopLevelItem(root)
        self.append_children(root, int(module["id"]))
        root.setExpanded(True)
        self.tree.setCurrentItem(root)

    def append_children(self, parent_item: QTreeWidgetItem, parent_id: int):
        if self.library_id is None:
            return
        parent_node = parent_item.data(0, Qt.UserRole) or {}
        parent_name = str(parent_node.get("name", "")).strip()
        parent_path = str(parent_node.get("path", "")).strip()
        for n in self.client.get_tree(self.library_id, parent_id=parent_id):
            node_name = str(n.get("name", "")).strip()
            node_path = str(n.get("path", "")).strip()
            # Avoid showing duplicated same-name/same-path layer not present in web tree.
            if (parent_name and node_name == parent_name and parent_path and node_path == parent_path) or (
                parent_name and node_name == parent_name and not parent_path
            ):
                continue
            item = QTreeWidgetItem([n["name"]]); item.setData(0, Qt.UserRole, n)
            parent_item.addChild(item)
            self.append_children(item, int(n["id"]))

    def on_tree_clicked(self, item: QTreeWidgetItem, _column: int = 0) -> None:
        self._apply_tree_node(item)

    def _apply_tree_node(self, item: QTreeWidgetItem) -> None:
        node = item.data(0, Qt.UserRole) or {}
        node_id = node.get("id")
        if self.library_id is None or node_id is None:
            return
        self.breadcrumb.setText(f"当前路径: {node.get('path', '-')}")
        self.assets = self.client.get_assets(self.library_id, node_id=int(node_id))
        self.render_assets()

    def _find_item_for_node_id(self, node_id: int) -> QTreeWidgetItem | None:
        def walk(wi: QTreeWidgetItem) -> QTreeWidgetItem | None:
            d = wi.data(0, Qt.UserRole) or {}
            if int(d.get("id", -1)) == int(node_id):
                return wi
            for c in range(wi.childCount()):
                r = walk(wi.child(c))
                if r is not None:
                    return r
            return None

        for t in range(self.tree.topLevelItemCount()):
            r = walk(self.tree.topLevelItem(t))
            if r is not None:
                return r
        return None

    @staticmethod
    def _expand_to_item(item: QTreeWidgetItem) -> None:
        p = item.parent()
        while p is not None:
            p.setExpanded(True)
            p = p.parent()

    def asset_thumb(self, asset: dict[str, Any]) -> QPixmap | None:
        rel = asset.get("thumbnail_relative_path")
        if not rel or self.library_id is None:
            return None
        key = f"{self.library_id}:{rel}"
        if key in self.thumb_cache:
            return self.thumb_cache[key]
        try:
            content = self.client.get_media_bytes(self.library_id, rel)
            px = QPixmap(); px.loadFromData(content)
            self.thumb_cache[key] = px
            return px
        except Exception:
            return None

    def render_assets(self) -> None:
        tw = int(self._card_thumb_w)
        th = int(tw * 118 // 210) if tw > 0 else 80
        row_h = max(64, th + 12)
        grid_w = tw + 30
        grid_h = th + 88
        li_sz = max(32, int(tw * 54 // 210))

        self.asset_list.clear()
        if self.view_mode == "list":
            self.asset_list.setViewMode(QListView.ListMode)
            self.asset_list.setGridSize(QSize(0, row_h))
            self.asset_list.setIconSize(QSize(li_sz, li_sz))
        else:
            self.asset_list.setViewMode(QListView.IconMode)
            self.asset_list.setGridSize(QSize(grid_w, grid_h))
            self.asset_list.setIconSize(QSize(tw, th))
        q = self.search_edit.text().strip().lower()
        items = [a for a in self.assets if not q or q in (a.get("display_name") or a.get("name", "")).lower()]
        try:
            fav_checked = self.fav_only_btn.isChecked()
        except Exception:
            fav_checked = False
        if fav_checked:
            items = [a for a in items if int(a.get("id")) in self.favorites]
        for a in items:
            aid = int(a.get("id"))
            title = a.get("display_name") or a.get("name", "-")
            subtitle = f"{a.get('status', '-')}" + (f" · {a.get('file_format')}" if a.get("file_format") else "")
            it = QListWidgetItem()
            it.setData(Qt.UserRole, a)
            if self.view_mode == "list":
                row = QWidget()
                rlay = QHBoxLayout(row)
                rlay.setContentsMargins(8, 6, 8, 6)
                thumb = QLabel()
                px = self.asset_thumb(a)
                thumb.setFixedSize(li_sz, li_sz)
                if px and not px.isNull():
                    thumb.setPixmap(px.scaled(li_sz, li_sz, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                else:
                    thumb.setText("-")
                text = QLabel(f"{title}\n{a.get('node_path') or '-'}")
                star = QToolButton()
                star.setText("★" if aid in self.favorites else "☆")
                star.setObjectName("cardStar")
                star.setAutoRaise(True)
                star.setCursor(Qt.PointingHandCursor)
                star.clicked.connect(lambda _=False, x=aid: self.toggle_favorite(x))
                rlay.addWidget(thumb)
                rlay.addWidget(text, 1)
                rlay.addWidget(star)
                it.setSizeHint(QSize(0, row_h))
                self.asset_list.addItem(it)
                self.asset_list.setItemWidget(it, row)
            else:
                card = AssetCardWidget(
                    title,
                    subtitle,
                    self.asset_thumb(a),
                    aid in self.favorites,
                    tw,
                    th,
                    lambda _=False, x=aid: self.toggle_favorite(x),
                )
                it.setSizeHint(QSize(grid_w, grid_h))
                self.asset_list.addItem(it)
                self.asset_list.setItemWidget(it, card)
        self.fav_only_btn.setText(f"仅看收藏({len(self.favorites)})")

        self._reselect_list_asset()

    def _reselect_list_asset(self) -> None:
        rid = getattr(self, "_reselect_after_render", None)
        if rid is not None:
            self._reselect_after_render = None
            for i in range(self.asset_list.count()):
                w_it = self.asset_list.item(i)
                d = w_it.data(Qt.UserRole) or {}
                if d and int(d.get("id", 0)) == int(rid):
                    self.asset_list.setCurrentItem(w_it)
                    break

    def toggle_favorite(self, asset_id: int) -> None:
        try:
            if asset_id in self.favorites:
                self.client.remove_favorite(asset_id)
                self.favorites.discard(asset_id)
            else:
                self.client.add_favorite(asset_id)
                self.favorites.add(asset_id)
        except Exception as exc:
            QMessageBox.warning(self, "收藏", str(exc))
            return
        try:
            self.fav_only_btn.setText(f"仅看收藏({len(self.favorites)})")
        except Exception:
            pass
        self._reselect_after_render = asset_id
        self.render_assets()

    def on_asset_clicked(self, item: QListWidgetItem) -> None:
        a = item.data(Qt.UserRole) or {}
        asset_id = a.get("id")
        if not asset_id:
            return
        int_aid = int(asset_id)
        self._reselect_after_render = int_aid
        nid = a.get("node_id")
        if nid is not None and self.library_id is not None:
            titem = self._find_item_for_node_id(int(nid))
            if titem is not None:
                self.tree.blockSignals(True)
                self._expand_to_item(titem)
                self.tree.setCurrentItem(titem)
                self.tree.scrollToItem(titem)
                self.tree.blockSignals(False)
            else:
                self._reselect_list_asset()
        else:
            self._reselect_list_asset()

        detail = self.client.get_asset_detail(int_aid)
        self.detail_name.setText(str(detail.get("display_name") or detail.get("name") or "—"))
        node_path = str(a.get("node_path") or "")
        if node_path:
            segs = [x for x in node_path.split("/") if x]
            self.detail_type.setText(" / ".join(segs[1:]) if len(segs) > 1 else node_path)
        else:
            self.detail_type.setText("—")
        files = detail.get("files", [])
        primary = files[0] if files else None
        if primary and isinstance(primary.get("relative_path"), str):
            ext = Path(primary["relative_path"]).suffix.upper().lstrip(".")
            self.detail_file_type.setText(ext or str(a.get("file_format") or "—"))
        else:
            self.detail_file_type.setText(str(a.get("file_format") or "—"))
        total_size = 0
        for f in files:
            try:
                total_size += int(f.get("size") or 0)
            except Exception:
                pass
        self.detail_file_size.setText(self._format_bytes(total_size if total_size > 0 else None))
        set_date = "-"
        for f in files:
            if f.get("mtime"):
                set_date = str(f["mtime"])
                break
        if set_date != "-":
            try:
                set_date = datetime.fromisoformat(set_date.replace("Z", "+00:00")).strftime("%Y/%m/%d %H:%M:%S")
            except Exception:
                pass
        self.detail_set_date.setText(set_date)
        self.detail_status.setText(str(detail.get("status") or "—"))
        preview_path = None
        lines: list[str] = ["Files:"]
        for f in files:
            rel = f.get("relative_path", "")
            lower = rel.lower()
            if preview_path is None and lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
                preview_path = rel
            mtime = f.get("mtime")
            if mtime:
                try:
                    mtime = datetime.fromisoformat(str(mtime).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
            lines.append(f"  • {rel} ({f.get('size', '-')}, {mtime or '-'})")
        self.detail_text.setPlainText("\n".join(lines) if len(lines) > 1 else "（无文件）")
        if preview_path and self.library_id is not None:
            try:
                content = self.client.get_media_bytes(self.library_id, preview_path)
                px = QPixmap()
                if px.loadFromData(content):
                    self.preview.set_preview_pixmap(px)
                else:
                    self.preview.set_preview_pixmap(None)
            except Exception:
                self.preview.set_preview_pixmap(None)
        else:
            self.preview.set_preview_pixmap(None)

    def on_asset_double_clicked(self, _item: QListWidgetItem) -> None:
        return

    def open_manage_dialog(self):
        if self.library_id is None:
            QMessageBox.warning(self, "提示", "尚未加载库")
            return
        dlg = ManageDialog(self)
        dlg.exec()


__all__ = ["DesktopWindow"]

