"""ColorScaleBar：色阶图例（参见《UI 设计》§6.2.3）。"""

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QFont
from PySide6.QtWidgets import QWidget

from .. import theme


class ColorScaleBar(QWidget):
    def __init__(self, base: str = "blue_red", vmin: float = 0.0, vmax: float = 500.0, unit: str = "kΩ", parent=None) -> None:
        super().__init__(parent)
        self.base = base
        self.vmin = vmin
        self.vmax = vmax
        self.unit = unit
        self.setFixedHeight(40)

    def set_range(self, vmin: float, vmax: float) -> None:
        self.vmin = vmin
        self.vmax = vmax
        self.update()

    def set_base(self, base: str) -> None:
        self.base = base
        self.update()

    def paintEvent(self, _evt) -> None:
        p = QPainter(self)
        L = theme.current()
        bar_rect = QRectF(0, 12, self.width() - 100, 16)
        stops = theme.COLOR_BASES.get(self.base, theme.COLOR_BASES["blue_red"])
        grad = QLinearGradient(bar_rect.left(), 0, bar_rect.right(), 0)
        n = len(stops)
        for i, c in enumerate(stops):
            grad.setColorAt(i / max(1, n - 1), QColor(c))
        p.fillRect(bar_rect, QBrush(grad))
        # 边框
        p.setPen(QColor(L["border_default"]))
        p.drawRect(bar_rect)
        # 端点标记
        p.setBrush(QColor(stops[0]))
        p.drawEllipse(bar_rect.left() - 4, bar_rect.center().y() - 4, 8, 8)
        p.setBrush(QColor(stops[-1]))
        p.drawEllipse(bar_rect.right() - 4, bar_rect.center().y() - 4, 8, 8)

        # 数字标签
        f = QFont()
        f.setPixelSize(theme.FONT_SIZE["small"])
        f.setFamily(theme.FONT_STACK["mono"])
        p.setFont(f)
        p.setPen(QColor(L["text_secondary"]))
        p.drawText(self.width() - 92, 14, f"{self.vmax:.0f}")
        p.drawText(self.width() - 92, 30, f"{self.vmin:.0f}")
        p.drawText(self.width() - 60, 22, self.unit)
        p.end()