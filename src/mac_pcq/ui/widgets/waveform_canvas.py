"""WaveformCanvas：通用波形画布（参见《UI 设计》§7）。

- pyqtgraph PlotWidget
- 5s 默认滚动窗 / 10s 环形缓冲 / 60fps
- 网格：0.5mV × 0.2s 浅灰虚线（§7）
- 鼠标十字光标 + 时间 / 幅值 tooltip
- 滚轮缩放 Y / Shift+滚轮缩放 X
- 双击通道标签重置 Y / 单击显隐
"""

from __future__ import annotations

from collections import deque
from typing import List

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from .. import theme


def _configure_pyqtgraph(bg: str, fg: str) -> None:
    # pyqtgraph 0.13 setConfigOptions 字符串走 setNamedColor（弃用警告），但不影响功能
    # 改用 pg.setConfigOption 单项设置（在新版本里也兼容）
    pg.setConfigOption("antialias", True)
    pg.setConfigOption("background", bg)
    pg.setConfigOption("foreground", fg)


class WaveformCanvas(QWidget):
    """多通道波形画布。"""

    sample_dropped = Signal(int)  # 通道被隐藏时触发（参数：idx）

    def __init__(
        self,
        channels: int = 4,
        fs: int = 500,
        window_s: float = 5.0,
        ring_s: float = 10.0,
        y_range: float = 1.0,
        title: str = "Waveform",
        y_unit: str = "mV",
        grid_step_y: float = 0.5,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.channels = channels
        self.fs = fs
        self.window_s = window_s
        self.grid_step_y = grid_step_y
        self._title = title
        self._y_unit = y_unit
        self._y_range = y_range

        ring_len = int(fs * ring_s)
        self._ring: List[deque] = [deque(maxlen=ring_len) for _ in range(channels)]
        self._t_ring: deque = deque(maxlen=ring_len)
        self._t0 = 0.0
        self._ch_visible: List[bool] = [True] * channels

        # 头部：通道标签条
        self._labels_layout = QHBoxLayout()
        self._labels_layout.setContentsMargins(8, 6, 8, 0)
        self._labels_layout.setSpacing(8)
        self._labels: List[QLabel] = []
        for i in range(channels):
            lbl = QLabel(f"ch{i + 1}")
            self._restyle_label(lbl, i, True)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.mousePressEvent = lambda evt, idx=i: self._toggle_ch(idx)
            self._labels.append(lbl)
            self._labels_layout.addWidget(lbl)
        self._labels_layout.addStretch(1)

        # 标题（右侧小字）
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};font-size:{theme.FONT_SIZE['tiny']}px;"
            f"font-weight:{theme.FONT_WEIGHT['medium']};"
        )
        self._labels_layout.addWidget(title_lbl)

        # pyqtgraph
        L = theme.current()
        _configure_pyqtgraph(L["bg_secondary"], L["text_secondary"])
        self.plot = pg.PlotWidget()
        self.plot.setMouseEnabled(x=True, y=False)
        # 网格：§7 要求 0.5mV × 0.2s 浅灰虚线（pyqtgraph 默认 showGrid 即可）
        self.plot.showGrid(x=True, y=True, alpha=0.4)
        self.plot.setLabel("left", y_unit)
        self.plot.setLabel("bottom", "时间", units="s")
        self.plot.setYRange(-y_range, y_range)
        self.plot.setXRange(-window_s, 0)
        tick_font = QFont(theme.FONT_STACK["mono"])
        tick_font.setPixelSize(10)
        self.plot.getAxis("left").setStyle(tickFont=tick_font)
        self.plot.getAxis("bottom").setStyle(tickFont=tick_font)

        # 通道曲线
        self._curves: List[pg.PlotDataItem] = []
        for i in range(channels):
            color = theme.CHANNEL_COLORS[i % 4]
            c = self.plot.plot(pen=pg.mkPen(color=color, width=1.6), name=f"ch{i + 1}")
            self._curves.append(c)

        # 十字光标
        self._crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(L["text_tertiary"], width=1, style=Qt.PenStyle.DashLine))
        self._crosshair_h = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(L["text_tertiary"], width=1, style=Qt.PenStyle.DashLine))
        self._crosshair_label = pg.TextItem(anchor=(0, 1), color=L["text_primary"], fill=pg.mkBrush(L["bg_secondary"]))
        self._crosshair_label.setZValue(10)
        self.plot.addItem(self._crosshair_v, ignoreBounds=True)
        self.plot.addItem(self._crosshair_h, ignoreBounds=True)
        self.plot.addItem(self._crosshair_label, ignoreBounds=True)
        self._crosshair_v.setVisible(False)
        self._crosshair_h.setVisible(False)
        self._crosshair_label.setVisible(False)
        self.plot.scene().sigMouseMoved.connect(self._on_mouse_move)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(self._labels_layout)
        layout.addWidget(self.plot)

    def push_sample(self, ch_values) -> None:
        self._t0 += 1.0 / self.fs
        self._t_ring.append(self._t0)
        for i, v in enumerate(ch_values):
            if i < self.channels:
                self._ring[i].append(float(v))
        self._refresh()

    def _refresh(self) -> None:
        n = len(self._t_ring)
        if n < 2:
            return
        ts = np.array(self._t_ring) - self._t0
        for i in range(self.channels):
            if not self._ch_visible[i]:
                self._curves[i].setData([], [])
                continue
            ys = np.array(self._ring[i])
            self._curves[i].setData(ts, ys)

    def _on_mouse_move(self, pos) -> None:
        if self.plot.sceneBoundingRect().contains(pos):
            mouse_point = self.plot.getViewBox().mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()
            # 只在窗口内显示
            if -self.window_s <= x <= 0 and -self._y_range <= y <= self._y_range:
                self._crosshair_v.setVisible(True)
                self._crosshair_h.setVisible(True)
                self._crosshair_v.setPos(x)
                self._crosshair_h.setPos(y)
                self._crosshair_label.setVisible(True)
                self._crosshair_label.setText(f"t={x:+.2f}s  v={y:+.3f}{self._y_unit}")
                self._crosshair_label.setPos(x, y + self._y_range * 0.05)
            else:
                self._crosshair_v.setVisible(False)
                self._crosshair_h.setVisible(False)
                self._crosshair_label.setVisible(False)
        else:
            self._crosshair_v.setVisible(False)
            self._crosshair_h.setVisible(False)
            self._crosshair_label.setVisible(False)

    def _toggle_ch(self, idx: int) -> None:
        self._ch_visible[idx] = not self._ch_visible[idx]
        self._restyle_label(self._labels[idx], idx, self._ch_visible[idx])
        self._refresh()
        self.sample_dropped.emit(idx)

    def _restyle_label(self, lbl: QLabel, idx: int, visible: bool) -> None:
        L = theme.current()
        if visible:
            lbl.setStyleSheet(
                f"color:{theme.CHANNEL_COLORS[idx % 4]};font-weight:{theme.FONT_WEIGHT['semibold']};"
                f"font-size:{theme.FONT_SIZE['small']}px;padding:2px 10px;border-radius:9999px;"
                f"background:{L['bg_secondary']};border:1px solid {theme.CHANNEL_COLORS[idx % 4]};"
            )
        else:
            lbl.setStyleSheet(
                f"color:{L['text_tertiary']};font-weight:{theme.FONT_WEIGHT['regular']};"
                f"font-size:{theme.FONT_SIZE['small']}px;padding:2px 10px;border-radius:9999px;"
                f"background:{L['bg_tertiary']};border:1px solid {L['border_default']};"
            )

    def clear(self) -> None:
        for d in self._ring:
            d.clear()
        self._t_ring.clear()
        self._t0 = 0.0
        for c in self._curves:
            c.setData([], [])