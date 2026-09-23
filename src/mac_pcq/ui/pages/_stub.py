"""Stub page 基类 v2：现代仪表盘风格，带 PageHeader。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame

from .. import theme
from ..widgets.icon import get_pixmap


class PageHeader(QWidget):
    """页头：标题 + 描述 + 右上角动作区。"""

    def __init__(self, title: str, subtitle: str = "", icon_name: str = "", parent=None) -> None:
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)

        # 图标
        if icon_name:
            ic = QLabel()
            ic.setPixmap(get_pixmap(icon_name, 32))
            ic.setFixedSize(32, 32)
            lay.addWidget(ic, 0, Qt.AlignmentFlag.AlignVCenter)

        # 标题块
        text_block = QVBoxLayout()
        text_block.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("PageHeader")
        text_block.addWidget(title_lbl)
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("PageSubtitle")
            sub_lbl.setWordWrap(True)
            text_block.addWidget(sub_lbl)
        lay.addLayout(text_block, 1)

        # 右上动作
        self._action_layout = QHBoxLayout()
        self._action_layout.setSpacing(8)
        lay.addLayout(self._action_layout)

        # 分隔线
        self._divider = QFrame()
        self._divider.setFrameShape(QFrame.Shape.HLine)
        self._divider.setFixedHeight(1)
        self._divider.setStyleSheet(f"background:{theme.current()['border_default']};")

    def add_action(self, btn) -> None:
        self._action_layout.addWidget(btn)

    def divider(self) -> QFrame:
        return self._divider


class StubPage(QWidget):
    """带 PageHeader 的占位页（给未实现的 P3-P6 等用）。"""

    TITLE: str = "Stub"
    DESC: str = "本页面将在后续迭代中实现"
    ICON: str = "info"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._title = self.TITLE
        self._desc = self.DESC
        self._icon = self.ICON
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = PageHeader(self._title, self._desc, self._icon)
        root.addWidget(header)
        root.addWidget(header.divider())

        # 空状态插画 + 提示
        empty = QWidget()
        el = QVBoxLayout(empty)
        el.setContentsMargins(0, 60, 0, 0)
        el.setSpacing(12)
        self._ic = QLabel()
        self._ic.setPixmap(get_pixmap(self._icon, 64))
        self._ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(self._ic, 0, Qt.AlignmentFlag.AlignHCenter)
        self._hint = QLabel("此页面将在下一轮迭代中实现")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};"
            f"font-size:{theme.FONT_SIZE['body']}px;"
        )
        el.addWidget(self._hint, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(empty, 1)

    def restyle(self) -> None:
        """主题切换：重设 hint 颜色（图标重画由 QSS 触发）。"""
        self._hint.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};"
            f"font-size:{theme.FONT_SIZE['body']}px;"
        )