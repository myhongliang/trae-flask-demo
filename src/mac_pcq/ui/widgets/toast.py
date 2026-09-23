"""Toast 反馈组件（参见《UI 设计》§5.5）。

- success 2s / failure 5s + 可点开
- 自动消失（非阻塞）
- 右下角堆叠滑入
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication

from .. import theme
from .icon import _svg_renderer


class ToastKind(Enum):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class _Colors:
    bg: str
    fg: str
    icon: str


_KIND_COLORS = {
    ToastKind.SUCCESS: ("#10B981", "white", "success"),
    ToastKind.INFO:    ("#3B82F6", "white", "info"),
    ToastKind.WARNING: ("#F59E0B", "white", "warning"),
    ToastKind.ERROR:   ("#EF4444", "white", "error"),
}


_TOAST_TEXTS = {
    ToastKind.SUCCESS: "成功",
    ToastKind.INFO:    "信息",
    ToastKind.WARNING: "告警",
    ToastKind.ERROR:   "错误",
}


class Toast(QWidget):
    """单条 toast。"""

    HEIGHT = 56
    WIDTH = 360

    def __init__(self, kind: ToastKind, message: str, duration_ms: int = 2000, parent=None) -> None:
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        bg, fg, icon_name = _KIND_COLORS[kind]
        self.kind = kind
        self.message = message
        self.duration_ms = duration_ms

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 图标
        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(20, 20)
        self._render_icon(icon_name, fg)
        layout.addWidget(self._icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        # 文案
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        title = QLabel(_TOAST_TEXTS[kind])
        title.setStyleSheet(f"color:{fg};font-weight:700;font-size:12px;")
        body = QLabel(message)
        body.setStyleSheet(f"color:{fg};font-size:13px;")
        body.setWordWrap(True)
        text_layout.addWidget(title)
        text_layout.addWidget(body)
        layout.addLayout(text_layout, 1)

        # 绘制背景
        self._bg_color = bg
        self._fg_color = fg

        # 自动关闭
        QTimer.singleShot(duration_ms, self._fade_out)

    def _render_icon(self, name: str, color: str) -> None:
        from PySide6.QtGui import QPixmap
        renderer = _svg_renderer(name)
        if renderer is None:
            return
        pix = QPixmap(20, 20)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor(color))
        p.setBrush(QColor(color))
        renderer.render(p)
        p.end()
        self._icon_lbl.setPixmap(pix)

    def paintEvent(self, _evt) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 圆角背景
        p.setBrush(QBrush(QColor(self._bg_color)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        p.end()

    def _fade_out(self) -> None:
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(200)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(self.deleteLater)
        anim.start()
        # 保留引用避免 GC
        self._anim = anim


# 静态管理器
_active: List[Toast] = []


def _position_toasts() -> None:
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    n = len(_active)
    for i, t in enumerate(_active):
        x = geo.right() - t.WIDTH - 24
        y = geo.bottom() - (i + 1) * (t.HEIGHT + 12) - 24
        t.move(x, y)
        t.show()
        # 保证 Toast 始终在最上层（不被 Modal 遮挡）
        t.raise_()


def show_toast(message: str, kind: ToastKind = ToastKind.INFO, duration_ms: Optional[int] = None) -> Toast:
    """全局便捷函数：右下角弹出一个 toast。"""
    if duration_ms is None:
        duration_ms = 2000 if kind in (ToastKind.SUCCESS, ToastKind.INFO) else 5000
    t = Toast(kind, message, duration_ms)
    _active.append(t)
    t.destroyed.connect(lambda: _active.remove(t) if t in _active else None)
    _position_toasts()
    return t


def success(message: str) -> Toast:
    return show_toast(message, ToastKind.SUCCESS, 2000)


def info(message: str) -> Toast:
    return show_toast(message, ToastKind.INFO, 2000)


def warning(message: str) -> Toast:
    return show_toast(message, ToastKind.WARNING, 5000)


def error(message: str) -> Toast:
    return show_toast(message, ToastKind.ERROR, 5000)