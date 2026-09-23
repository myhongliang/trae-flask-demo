"""SVG 图标加载器 + Icon 组件。

所有图标用 currentColor，主题切换自动跟随。
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel

from .. import theme

ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")


@lru_cache(maxsize=64)
def _svg_renderer(name: str) -> Optional[QSvgRenderer]:
    path = os.path.join(ICONS_DIR, f"{name}.svg")
    if not os.path.isfile(path):
        return None
    renderer = QSvgRenderer(path)
    if not renderer.isValid():
        return None
    return renderer


def get_icon(name: str, color: Optional[str] = None, size: int = 16) -> QIcon:
    """返回带颜色（默认 currentColor / 主题 text_primary）的 QIcon。

    QSvg 不直接渲染 currentColor，因此我们手动用前景色画一份。
    """
    renderer = _svg_renderer(name)
    if renderer is None:
        return QIcon()
    if color is None:
        color = theme.current()["text_primary"]
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(color))
        painter.setBrush(QColor(color))
        renderer.render(painter)
    finally:
        painter.end()
    return QIcon(pix)


def get_pixmap(name: str, size: int = 16) -> QPixmap:
    """返回透明背景的图标 pixmap（用于嵌入 QSS 的 qproperty-icon）。"""
    renderer = _svg_renderer(name)
    if renderer is None:
        return QPixmap()
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    return pix


class IconLabel(QLabel):
    """可显示 SVG 图标的标签，自动跟随主题。"""

    def __init__(self, name: str, size: int = 16, parent=None) -> None:
        super().__init__(parent)
        self._name = name
        self._size = size
        self.setFixedSize(QSize(size + 4, size + 4))
        self.refresh()

    def set_icon_name(self, name: str) -> None:
        self._name = name
        self.refresh()

    def refresh(self) -> None:
        color = theme.current()["text_primary"]
        renderer = _svg_renderer(self._name)
        if renderer is None:
            return
        from PySide6.QtGui import QPixmap
        pix = QPixmap(self._size, self._size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor(color))
        p.setBrush(QColor(color))
        renderer.render(p)
        p.end()
        self.setPixmap(pix)