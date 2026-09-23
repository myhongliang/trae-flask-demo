"""MainWindow v2：现代仪表盘风格。

- 顶栏 56px：Logo + 标题 + 链路指示灯 + 状态徽章 + 主题切换 + 设置 + 帮助
- 侧栏 220px：9 个页面入口（图标 + 文字 + 选中色条）
- 主区：当前页面
- 底栏 56px：开始 / 停止 / 导出 + 状态文字
- 快捷键 Ctrl+O/S/E / F1/F5 / Esc / 1~9
- 主题切换调用 stylesheet.render_qss() 重注全局 QSS
"""

from __future__ import annotations

from typing import List, Tuple

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QStackedWidget, QFrame, QStatusBar,
    QPushButton,
)

from .widgets.link_indicator import LinkIndicator
from .widgets.status_badge import StatusBadge
from .widgets.icon import get_pixmap
from .widgets.buttons import PrimaryButton, DangerButton, SecondaryButton
from .widgets.toast import success as toast_success
from .pages.monitor import PageMonitor
from .pages.resistive import PageResistive
from .pages.piezo import PagePiezo
from .pages.vital import PageVital
from .pages.record import PageRecord
from .pages.device import PageDevice
from .pages.config import PageConfig
from .pages.upgrade import PageUpgrade
from .pages.log import PageLog
from mac_pcq.ui import theme
from .stylesheet import render_qss


# 9 个页面（图标 + 类）
_NAV: List[Tuple[str, str, type]] = [
    ("主监测",  "monitor",   PageMonitor),
    ("压阻矩阵", "matrix",    PageResistive),
    ("压电波形", "waveform",  PagePiezo),
    ("生命体征", "heart",     PageVital),
    ("记录回放", "record",    PageRecord),
    ("设备状态", "device",    PageDevice),
    ("参数配置", "config",    PageConfig),
    ("固件升级", "upgrade",   PageUpgrade),
    ("日志",    "log",       PageLog),
]


class MainWindow(QMainWindow):
    def __init__(self, app_controller=None, parent=None) -> None:
        super().__init__(parent)
        self.app = app_controller
        self.setWindowTitle("多模态采集板上住机  v0.1")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 640)

        self._build()
        # 默认选第一页
        self.nav_list.setCurrentRow(0)

        # 全局 QSS（style.qss + token 替换）
        # 注意：这里直接设置到 QApplication；stylesheet.apply_global 由 main.py 调用
        self._restyle_nav()

        # 主题切换时整体 restyle
        theme.subscribe(self._on_theme_changed)

        # 快捷键
        self._install_shortcuts()

    def _build(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 顶栏
        root_layout.addWidget(self._build_topbar())
        # 主区（侧栏 + 内容）
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidenav())
        body.addWidget(self._build_center(), 1)
        body_widget = QWidget()
        body_widget.setLayout(body)
        body_widget.setObjectName("BodyContainer")
        root_layout.addWidget(body_widget, 1)
        # 底栏
        root_layout.addWidget(self._build_bottombar())

        # 状态栏
        self.setStatusBar(QStatusBar())

    # ---- 顶栏 ----
    def _build_topbar(self) -> QWidget:
        topbar = QWidget()
        topbar.setObjectName("TopBar")
        topbar.setFixedHeight(56)
        lay = QHBoxLayout(topbar)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(16)

        # Logo
        self._logo = QLabel()
        self._logo.setPixmap(get_pixmap("logo", 24))
        self._logo.setFixedSize(24, 24)
        lay.addWidget(self._logo, 0, Qt.AlignmentFlag.AlignVCenter)

        title = QLabel("多模态采集板上住机")
        title.setObjectName("LogoTitle")
        title_font = QFont()
        title_font.setPixelSize(theme.FONT_SIZE["h3"])
        title_font.setBold(True)
        title.setFont(title_font)
        lay.addWidget(title, 0, Qt.AlignmentFlag.AlignVCenter)

        ver = QLabel("v0.1")
        ver.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};"
            f"font-size:{theme.FONT_SIZE['small']}px;"
            f"background:transparent;border:0;"
            f"padding:2px 8px;border-radius:9999px;"
        )
        lay.addWidget(ver, 0, Qt.AlignmentFlag.AlignVCenter)

        lay.addStretch(1)

        # 右侧：状态指示 + 徽章 + 主题 + 设置 + 帮助
        self.link_ind = LinkIndicator()
        lay.addWidget(self.link_ind)

        self.status_badge = StatusBadge()
        lay.addWidget(self.status_badge)

        # 分隔
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(24)
        sep.setStyleSheet(f"color:{theme.current()['border_default']};")
        lay.addWidget(sep)

        # 主题切换
        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("ThemeToggle")
        self._theme_btn.setIcon(get_pixmap("sun", 16))
        self._theme_btn.setIconSize(QSize(16, 16))
        self._theme_btn.setFixedSize(32, 32)
        self._theme_btn.setToolTip("切换主题（当前：暗色）")
        self._theme_btn.clicked.connect(self._toggle_theme)
        lay.addWidget(self._theme_btn)

        # 设置
        settings_btn = QPushButton()
        settings_btn.setObjectName("SettingsButton")
        settings_btn.setIcon(get_pixmap("settings", 16))
        settings_btn.setIconSize(QSize(16, 16))
        settings_btn.setFixedSize(32, 32)
        settings_btn.setToolTip("设置")
        lay.addWidget(settings_btn)

        # 帮助
        help_btn = QPushButton()
        help_btn.setObjectName("SettingsButton")
        help_btn.setIcon(get_pixmap("help", 16))
        help_btn.setIconSize(QSize(16, 16))
        help_btn.setFixedSize(32, 32)
        help_btn.setToolTip("帮助 (F1)")
        lay.addWidget(help_btn)

        return topbar

    # ---- 侧栏 ----
    def _build_sidenav(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("SideNav")
        wrap.setFixedWidth(220)
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.setSpacing(0)

        # Logo/品牌区
        brand = QWidget()
        brand.setObjectName("Brand")
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(4)
        self._brand_title = QLabel("采集控制台")
        self._brand_title.setStyleSheet(
            f"color:{theme.current()['text_primary']};"
            f"font-size:{theme.FONT_SIZE['h3']}px;"
            f"font-weight:{theme.FONT_WEIGHT['semibold']};"
            f"background:transparent;border:0;"
        )
        self._brand_sub = QLabel("Multimodal Acquisition")
        self._brand_sub.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};"
            f"font-size:{theme.FONT_SIZE['tiny']}px;"
            f"background:transparent;border:0;"
        )
        bl.addWidget(self._brand_title)
        bl.addWidget(self._brand_sub)
        lay.addWidget(brand)

        # 分隔
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{theme.current()['border_default']};")
        lay.addWidget(sep)

        # 列表
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("NavList")
        for i, (name, icon_name, _cls) in enumerate(_NAV):
            it = QListWidgetItem(f"  {name}")  # 前置空格给图标位置留
            it.setData(Qt.ItemDataRole.UserRole, i)
            it.setIcon(get_pixmap(icon_name, 16))
            self.nav_list.addItem(it)
        self.nav_list.setFixedWidth(220)
        font = QFont()
        font.setPixelSize(theme.FONT_SIZE["body"])
        font.setBold(False)
        self.nav_list.setFont(font)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        lay.addWidget(self.nav_list, 1)

        # 底部：版本
        foot = QLabel("build 0.1.0  ·  proto 1.0")
        foot.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};"
            f"font-size:{theme.FONT_SIZE['tiny']}px;"
            f"background:transparent;border:0;"
            f"padding:8px 20px;"
        )
        lay.addWidget(foot)

        return wrap

    # ---- 主区 ----
    def _build_center(self) -> QWidget:
        self.stack = QStackedWidget()
        self.stack.setObjectName("PageStack")
        self.pages = []
        for _name, _icon, cls in _NAV:
            page = cls()
            self.pages.append(page)
            self.stack.addWidget(page)
        return self.stack

    # ---- 底栏 ----
    def _build_bottombar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("BottomBar")
        bar.setFixedHeight(56)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)

        # 左侧：链路方式
        self._link_info = QLabel("USB-CDC  ·  SimMock")
        self._link_info.setStyleSheet(
            f"color:{theme.current()['text_secondary']};"
            f"font-size:{theme.FONT_SIZE['small']}px;"
            f"background:transparent;border:0;"
        )
        lay.addWidget(self._link_info)

        self._rec_dot = QLabel()
        self._rec_dot.setFixedSize(8, 8)
        self._rec_dot.setStyleSheet(
            f"background:{theme.current()['accent_danger']};"
            f"border-radius:4px;"
        )
        self._rec_dot.setVisible(False)
        lay.addSpacing(16)
        lay.addWidget(self._rec_dot)
        self._rec_lbl = QLabel("录制中")
        self._rec_lbl.setStyleSheet(
            f"color:{theme.current()['accent_danger']};"
            f"font-size:{theme.FONT_SIZE['small']}px;"
            f"font-weight:{theme.FONT_WEIGHT['semibold']};"
            f"background:transparent;border:0;"
        )
        self._rec_lbl.setVisible(False)
        lay.addWidget(self._rec_lbl)

        lay.addStretch(1)

        # 右侧：操作按钮
        self._start_btn = DangerButton("开始采集", icon="record")
        self._stop_btn = SecondaryButton("停止", icon="stop")
        self._stop_btn.setEnabled(False)
        self._export_btn = PrimaryButton("导出 CSV", icon="download")
        lay.addWidget(self._start_btn)
        lay.addWidget(self._stop_btn)
        lay.addWidget(self._export_btn)

        self._start_btn.clicked.connect(self._on_start_clicked)
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        self._export_btn.clicked.connect(lambda: toast_success("导出功能占位（下一轮实现）"))

        return bar

    # ---- 交互 ----
    def _on_nav_changed(self, idx: int) -> None:
        if 0 <= idx < self.stack.count():
            self.stack.setCurrentIndex(idx)
            name = _NAV[idx][0]
            self.statusBar().showMessage(f"页面：{name}", 1500)

    def goto(self, page_index: int) -> None:
        if 0 <= page_index < self.nav_list.count():
            self.nav_list.setCurrentRow(page_index)

    def _toggle_theme(self) -> None:
        new = theme.toggle()
        # 顶栏图标
        self._theme_btn.setIcon(get_pixmap("moon" if new == "dark" else "sun", 16))
        self._theme_btn.setToolTip(f"切换主题（当前：{'暗色' if new == 'dark' else '浅色'}）")

    def _on_theme_changed(self, _name: str) -> None:
        """主题切换：重注 QSS + 遍历所有页面调用 restyle()（同步 inline style）。"""
        L = theme.current()
        # 重新应用 QSS 到本窗口
        self.style().unpolish(self)
        self.style().polish(self)
        # 强制各 widget repaint
        for w in (self.link_ind, self.status_badge, self._link_info, self._rec_lbl,
                  self._brand_title, self._brand_sub, self._theme_btn):
            if w is not None:
                w.update()
        # 遍历所有页面（确保主题切换后 GroupBox / inline style / ParamForm 同步刷新）
        for page in getattr(self, "pages", []):
            restyle = getattr(page, "restyle", None)
            if callable(restyle):
                try:
                    page.restyle()
                except Exception:  # noqa: BLE001
                    pass

    def _install_shortcuts(self) -> None:
        for i in range(1, 10):
            act = QAction(self)
            act.setShortcut(QKeySequence(str(i)))
            act.triggered.connect(lambda _checked=False, idx=i - 1: self.goto(idx))
            self.addAction(act)
        for keys, slot in [
            ("Ctrl+O", lambda: self.statusBar().showMessage("打开文件…", 1500)),
            ("Ctrl+S", self._toggle_record),
            ("Ctrl+E", lambda: toast_success("导出 CSV 占位（下一轮实现）")),
            ("F1", lambda: self.statusBar().showMessage("帮助（占位）", 1500)),
            ("F5", lambda: self.statusBar().showMessage("刷新", 1500)),
            ("Esc", lambda: self.statusBar().clearMessage()),
        ]:
            act = QAction(self)
            act.setShortcut(QKeySequence(keys))
            act.triggered.connect(slot)
            self.addAction(act)

    def _on_start_clicked(self) -> None:
        self._rec_dot.setVisible(True)
        self._rec_lbl.setVisible(True)
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        toast_success("已开始采集")

    def _on_stop_clicked(self) -> None:
        self._rec_dot.setVisible(False)
        self._rec_lbl.setVisible(False)
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        toast_success("已停止采集")

    def _toggle_record(self) -> None:
        if self._start_btn.isEnabled():
            self._on_start_clicked()
        else:
            self._on_stop_clicked()

    def _restyle_nav(self) -> None:
        # 让 QListWidget item icon 跟随主题色（icon 已是 currentColor 友好）
        pass

    # ---- 给 AppController 调用 ----
    def get_monitor_page(self) -> PageMonitor:
        return self.pages[0]

    def get_page_index(self, name: str) -> int:
        for i, (n, _ic, _cls) in enumerate(_NAV):
            if n == name:
                return i
        raise KeyError(name)