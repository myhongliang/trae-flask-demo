"""MatrixGrid：4×4 压阻热力图（参见《UI 设计》§6.2 + §8）。

- 单元 60×60（缩略）/ 80×80（详情），间距 2px
- 悬停放大 + tooltip
- 色阶 6 基色
- 数值右下角小字
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtWidgets import QWidget

from .. import theme


def _interpolate(c1: str, c2: str, t: float) -> QColor:
    a = QColor(c1)
    b = QColor(c2)
    return QColor(
        int(a.red() * (1 - t) + b.red() * t),
        int(a.green() * (1 - t) + b.green() * t),
        int(a.blue() * (1 - t) + b.blue() * t),
    )


def value_to_color(value: float, vmin: float, vmax: float, base: str) -> QColor:
    if vmax <= vmin:
        t = 0.5
    else:
        t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    stops = theme.COLOR_BASES.get(base, theme.COLOR_BASES["blue_red"])
    pos = t * (len(stops) - 1)
    idx = int(pos)
    frac = pos - idx
    if idx >= len(stops) - 1:
        return QColor(stops[-1])
    return _interpolate(stops[idx], stops[idx + 1], frac)


class MatrixGrid(QWidget):
    def __init__(
        self,
        cell: int = 60,
        gap: int = 2,
        base: str = "blue_red",
        vmin: float = 10.0,
        vmax: float = 500.0,
        unit: str = "kΩ",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.cell = cell
        self.gap = gap
        self.base = base
        self.vmin = vmin
        self.vmax = vmax
        self.unit = unit
        self._values = [0.0] * 16
        self._hover_idx: Optional[int] = None
        self._selected: Optional[int] = None
        self._hover_scale: float = 1.0
        self._hover_anim: Optional[QPropertyAnimation] = None
        self.setFixedSize(4 * cell + 3 * gap, 4 * cell + 3 * gap)
        self.setMouseTracking(True)

    def set_values(self, values_16) -> None:
        if len(values_16) != 16:
            return
        self._values = list(values_16)
        self.update()

    def set_range(self, vmin: float, vmax: float) -> None:
        self.vmin = vmin
        self.vmax = vmax
        self.update()

    def set_base(self, base: str) -> None:
        self.base = base
        self.update()

    def set_selected(self, idx: Optional[int]) -> None:
        self._selected = idx
        self.update()

    def selected(self) -> Optional[int]:
        return self._selected

    def _animate_hover(self, on: bool) -> None:
        if self._hover_anim:
            self._hover_anim.stop()
        anim = QPropertyAnimation(self, b"hover_scale")
        anim.setDuration(theme.DURATION["fast"])
        anim.setStartValue(self._hover_scale)
        anim.setEndValue(1.15 if on else 1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._hover_anim = anim

    def get_hover_scale(self) -> float:
        return self._hover_scale

    def set_hover_scale(self, v: float) -> None:
        self._hover_scale = v
        self.update()

    # Qt 元对象系统识别的属性（供 QPropertyAnimation 使用）
    hover_scale = Property(float, get_hover_scale, set_hover_scale)

    def paintEvent(self, _evt) -> None:
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            L = theme.current()
            # 整体平移让 hover 放大不超出容器
            # 简化：hover 放大 = 在原位置缩放绘制
            cx_offsets = [0] * 16
            cy_offsets = [0] * 16
            if self._hover_idx is not None:
                row = self._hover_idx // 4
                col = self._hover_idx % 4
                cx = col * (self.cell + self.gap) + self.cell // 2
                cy = row * (self.cell + self.gap) + self.cell // 2
                # 整体平移让 hover 居中
                p.translate(cx, cy)
                p.scale(self._hover_scale, self._hover_scale)
                p.translate(-cx, -cy)

            for i in range(16):
                row, col = i // 4, i % 4
                x = col * (self.cell + self.gap)
                y = row * (self.cell + self.gap)
                color = value_to_color(self._values[i], self.vmin, self.vmax, self.base)
                p.setBrush(QBrush(color))
                if i == self._selected:
                    pen_color = QColor(L["accent_warning"])
                    pen_w = 3
                elif self._hover_idx == i:
                    pen_color = QColor(L["brand_primary"])
                    pen_w = 2
                else:
                    pen_color = QColor(L["border_default"])
                    pen_w = 1
                p.setPen(QPen(pen_color, pen_w))
                p.drawRect(x, y, self.cell, self.cell)
                # 数值
                p.setPen(QColor(L["text_primary"]))
                f = QFont()
                f.setPixelSize(11)
                f.setWeight(QFont.Weight.Medium)
                p.setFont(f)
                txt = f"{self._values[i]:.1f}"
                text_rect = QRectF(x + 4, y + self.cell - 18, self.cell - 8, 14)
                p.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, txt)
        finally:
            p.end()

    def mouseMoveEvent(self, evt) -> None:
        pos = evt.position() if hasattr(evt, "position") else QPointF(evt.pos())
        x, y = int(pos.x()), int(pos.y())
        col = x // (self.cell + self.gap)
        row = y // (self.cell + self.gap)
        if 0 <= row < 4 and 0 <= col < 4:
            idx = row * 4 + col
            if idx != self._hover_idx:
                self._hover_idx = idx
                self.setToolTip(f"通道 {idx + 1}：{self._values[idx]:.2f} {self.unit}")
                self._animate_hover(True)
        else:
            if self._hover_idx is not None:
                self._animate_hover(False)
            self._hover_idx = None
            self.setToolTip("")
        self.update()

    def leaveEvent(self, _evt) -> None:
        if self._hover_idx is not None:
            self._animate_hover(False)
        self._hover_idx = None
        self.setToolTip("")
        self.update()