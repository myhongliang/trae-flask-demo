"""StatusBadge：状态徽章（参见《UI 设计》§5.1）。

- 文字 + SVG 图标
- 颜色映射 token
- 圆角胶囊形（pill）
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from ...domain.session import SessionState
from .. import theme
from .icon import get_pixmap


_STATE = {
    SessionState.IDLE:      ("text_tertiary", "空闲",      "pause"),
    SessionState.STARTING:  ("accent_warning", "启动中",  "settings"),
    SessionState.RUNNING:   ("accent_success", "采集中",  "waveform"),
    SessionState.PAUSED:    ("text_secondary", "已暂停",  "pause"),
    SessionState.RECORDING: ("accent_danger",  "录制中",  "record"),
    SessionState.STOPPING:  ("accent_warning", "停止中",  "stop"),
    SessionState.ERROR:     ("accent_danger",  "错误",    "warning"),
}


class StatusBadge(QWidget):
    HEIGHT = 26

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._state = SessionState.IDLE
        self._build()
        self._refresh()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 12, 4)
        layout.setSpacing(6)
        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(14, 14)
        self._text_lbl = QLabel()
        font = QFont()
        font.setPixelSize(theme.FONT_SIZE["small"])
        font.setWeight(QFont.Weight.Medium)
        self._text_lbl.setFont(font)
        layout.addWidget(self._icon_lbl)
        layout.addWidget(self._text_lbl)
        self.setFixedHeight(self.HEIGHT)
        self.setMinimumWidth(80)

    def set_state(self, s: SessionState) -> None:
        self._state = s
        self._refresh()

    def _refresh(self) -> None:
        color_key, text, icon_name = _STATE[self._state]
        L = theme.current()
        # 背景：对应颜色的 15% 透明度版本
        bg = QColor(L[color_key])
        bg.setAlphaF(0.15)
        self.setStyleSheet(
            f"background:{bg.name(QColor.NameFormat.HexArgb)};"
            f"border:1px solid {QColor(L[color_key]).name()};"
            f"border-radius:{self.HEIGHT // 2}px;"
        )
        fg = L[color_key]
        self._text_lbl.setStyleSheet(f"color:{fg};border:0;background:transparent;")
        self._text_lbl.setText(text)
        # 图标
        pix = get_pixmap(icon_name, 14)
        # 染色
        from PySide6.QtGui import QPainter
        colored = QPixmap(pix.size())
        colored.fill(Qt.GlobalColor.transparent)
        p = QPainter(colored)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.setBrush(QColor(fg))
        p.drawPixmap(0, 0, pix)
        p.end()
        self._icon_lbl.setPixmap(colored)

    def paintEvent(self, _evt) -> None:
        # 背景由 QSS 控制，这里空实现避免 widget 自身绘制干扰
        pass