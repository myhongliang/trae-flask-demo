"""统一按钮组件（参见《UI 设计》§5.3）。

变体：primary / secondary / danger / ghost
尺寸：small 32 / medium 40 / large 48
最小宽度 64，圆角 radius_sm
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from .. import theme


class PrimaryButton(QPushButton):
    def __init__(self, text: str = "", parent=None, size: str = "md", icon=None) -> None:
        super().__init__(text, parent)
        self.setProperty("variant", "primary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_size(size)
        if icon:
            from .icon import get_icon
            self.setIcon(get_icon(icon))

    def _apply_size(self, size: str) -> None:
        h = theme.BUTTON.get(f"height_{size}", theme.BUTTON["height_md"])
        self.setMinimumHeight(h)
        self.setMinimumWidth(theme.BUTTON["min_width"])


class SecondaryButton(QPushButton):
    def __init__(self, text: str = "", parent=None, size: str = "md", icon=None) -> None:
        super().__init__(text, parent)
        self.setProperty("variant", "secondary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_size(size)
        if icon:
            from .icon import get_icon
            self.setIcon(get_icon(icon))

    def _apply_size(self, size: str) -> None:
        h = theme.BUTTON.get(f"height_{size}", theme.BUTTON["height_md"])
        self.setMinimumHeight(h)
        self.setMinimumWidth(theme.BUTTON["min_width"])


class DangerButton(QPushButton):
    def __init__(self, text: str = "", parent=None, size: str = "md", icon=None) -> None:
        super().__init__(text, parent)
        self.setProperty("variant", "danger")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_size(size)
        if icon:
            from .icon import get_icon
            self.setIcon(get_icon(icon))

    def _apply_size(self, size: str) -> None:
        h = theme.BUTTON.get(f"height_{size}", theme.BUTTON["height_md"])
        self.setMinimumHeight(h)
        self.setMinimumWidth(theme.BUTTON["min_width"])


class GhostButton(QPushButton):
    """工具栏按钮：透明背景，hover 时浅灰。"""
    def __init__(self, text: str = "", parent=None, size: str = "sm", icon=None) -> None:
        super().__init__(text, parent)
        self.setProperty("variant", "ghost")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_size(size)
        if icon:
            from .icon import get_icon
            self.setIcon(get_icon(icon))

    def _apply_size(self, size: str) -> None:
        h = theme.BUTTON.get(f"height_{size}", theme.BUTTON["height_sm"])
        self.setMinimumHeight(h)
        self.setMinimumWidth(0)


class IconButton(QPushButton):
    """仅图标按钮（方形）。"""
    def __init__(self, icon_name: str, tooltip: str = "", parent=None, size: int = 32) -> None:
        super().__init__("", parent)
        from .icon import get_icon
        self.setIcon(get_icon(icon_name))
        self.setIconSize(self.sizeHint().height() - 8)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        # 用 ghost 样式但允许 qproperty-icon
        self.setProperty("variant", "ghost")