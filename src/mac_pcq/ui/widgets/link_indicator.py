"""LinkIndicator：链路状态指示灯（参见《UI 设计》§5.2）。

- 4 状态：🟢已连接/采集中 / 🟡连接中 / 🔴错误 / ⚪未连接
- 颜色用 Token；连接中时黄色脉动动画
- SVG 图标 + tooltip
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

from ...transport.adapter import LinkState
from .. import theme


_STATE_STYLE = {
    LinkState.DISCONNECTED: ("text_tertiary", "未连接"),
    LinkState.CONNECTING:   ("accent_warning", "连接中"),
    LinkState.CONNECTED:    ("accent_success", "已连接"),
    LinkState.STREAMING:    ("accent_success", "采集中"),
    LinkState.UPGRADING:    ("accent_info", "升级中"),
    LinkState.ERROR:        ("accent_danger", "错误"),
}

_STATE_ICON = {
    LinkState.DISCONNECTED: "link_off",
    LinkState.CONNECTING:   "usb",
    LinkState.CONNECTED:    "link",
    LinkState.STREAMING:    "link",
    LinkState.UPGRADING:    "upgrade",
    LinkState.ERROR:        "error",
}


class LinkIndicator(QWidget):
    """圆点 + 图标 + tooltip；连接中脉动。"""

    DIAMETER = 12
    SIZE = 28

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._state = LinkState.DISCONNECTED
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setToolTip(self._label())
        self._anim: Optional[QPropertyAnimation] = None
        self._build_animation()

    def _label(self) -> str:
        return _STATE_STYLE.get(self._state, ("text_tertiary", ""))[1]

    def _color_key(self) -> str:
        return _STATE_STYLE.get(self._state, "text_tertiary")[0]

    def set_state(self, s: LinkState) -> None:
        self._state = s
        self.setToolTip(self._label())
        if s == LinkState.CONNECTING and self._anim:
            self._anim.start()
        elif self._anim and self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
            self.setOpacity(1.0)
        self.update()

    def _build_animation(self) -> None:
        anim = QPropertyAnimation(self, b"opacity")
        anim.setDuration(900)
        anim.setStartValue(1.0)
        anim.setEndValue(0.4)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.setLoopCount(-1)
        # 通过反向让它循环
        from PySide6.QtCore import QAbstractAnimation
        # 用 BindingLoop 替代：start/stop 切方向
        anim.finished.connect(lambda: None)
        self._anim = anim

    def setOpacity(self, v: float) -> None:
        self._opacity = v
        self.update()

    def paintEvent(self, _evt) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        L = theme.current()
        op = getattr(self, "_opacity", 1.0)
        color = QColor(L[self._color_key()])
        color.setAlphaF(op)
        # 圆点
        pad = (self.SIZE - self.DIAMETER) // 2
        # 外圈（halo）
        halo = QColor(color)
        halo.setAlphaF(0.25 * op)
        p.setBrush(halo)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(pad - 2, pad - 2, self.DIAMETER + 4, self.DIAMETER + 4)
        # 实心点
        p.setBrush(color)
        p.setPen(color.darker(120))
        p.drawEllipse(pad, pad, self.DIAMETER, self.DIAMETER)
        p.end()