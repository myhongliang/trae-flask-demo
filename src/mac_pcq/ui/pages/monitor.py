"""P1 - 主监测页 v2（现代仪表盘）。

布局：
    PageHeader
    左上：4 路 ECG（WaveformCanvas + 网格 + 十字光标）
    右上：矩阵缩略（MatrixGrid 60×60 + ColorScaleBar）
    左下：2 路 PVDF
    右下：VitalCard（HR/RR 大字 + 呼吸式动画）
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame,
)

from ..widgets.waveform_canvas import WaveformCanvas
from ..widgets.matrix_grid import MatrixGrid
from ..widgets.color_scale_bar import ColorScaleBar
from ..widgets.vital_card import VitalCard
from .. import theme
from ..widgets.icon import get_pixmap
from ._stub import PageHeader
from ...core.constants import DEFAULT_ECG_FS, DEFAULT_PVDF_FS


class _Panel(QFrame):
    """带标题 + 阴影的卡片容器。"""

    def __init__(self, title: str, body: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        L = theme.current()
        self.setStyleSheet(
            f"#Panel{{background:{L['bg_secondary']};"
            f"border:1px solid {L['border_default']};"
            f"border-radius:{theme.RADIUS['md']}px;"
            f"}}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("PanelTitle")
        lay.addWidget(title_lbl)
        lay.addWidget(body, 1)


class PageMonitor(QWidget):
    def __init__(
        self,
        ecg_fs: int = DEFAULT_ECG_FS,
        pvdf_fs: int = DEFAULT_PVDF_FS,
        parent=None,
    ) -> None:
        super().__init__(parent)
        L = theme.current()

        # ==== PageHeader ====
        header = PageHeader(
            "主监测",
            "4 路 ECG + 矩阵缩略 + 压电波形 + 生命体征 · 实时数据",
            "monitor",
        )
        # 右侧动作：录制 / 导出
        from ..widgets.buttons import PrimaryButton, SecondaryButton, DangerButton
        self._record_btn = DangerButton("开始录制", icon="record", size="sm")
        self._export_btn = SecondaryButton("导出", icon="download", size="sm")
        header.add_action(self._record_btn)
        header.add_action(self._export_btn)

        # ==== 内容 ====
        self.ecg = WaveformCanvas(
            channels=4, fs=ecg_fs, window_s=5.0, y_range=1.0,
            title="ECG (mV)",
        )
        self.piezo = WaveformCanvas(
            channels=2, fs=pvdf_fs, window_s=5.0, y_range=10.0,
            title="PVDF (mV)",
        )
        self.matrix = MatrixGrid(cell=60, gap=4, base="blue_red", vmin=10, vmax=500, unit="kΩ")
        self.scale_bar = ColorScaleBar(base="blue_red", vmin=10, vmax=500, unit="kΩ")
        self.vital = VitalCard()

        # 矩阵 + 色阶 容器
        matrix_body = QWidget()
        mb_lay = QVBoxLayout(matrix_body)
        mb_lay.setContentsMargins(0, 0, 0, 0)
        mb_lay.setSpacing(12)
        mb_lay.addWidget(self.matrix, 0, Qt.AlignmentFlag.AlignCenter)
        mb_lay.addWidget(self.scale_bar)
        mb_lay.addStretch(1)

        # 4 个 panel
        ecg_panel = _Panel("心电 (ECG)", self.ecg)
        matrix_panel = _Panel("矩阵缩略", matrix_body)
        piezo_panel = _Panel("压电 (PVDF)", self.piezo)
        vital_panel = _Panel("生命体征", self.vital)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        grid.addWidget(ecg_panel, 0, 0)
        grid.addWidget(matrix_panel, 0, 1)
        grid.addWidget(piezo_panel, 1, 0)
        grid.addWidget(vital_panel, 1, 1)
        grid.setRowStretch(0, 3)
        grid.setRowStretch(1, 2)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 1)

        # ==== 布局 ====
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)
        root.addWidget(header)
        root.addWidget(header.divider())
        root.addLayout(grid, 1)

    # ---- 槽函数 ----
    def on_ecg(self, sample) -> None:
        self.ecg.push_sample(sample.ch)

    def on_piezo(self, sample) -> None:
        self.piezo.push_sample(sample.ch)

    def on_resistive(self, sample) -> None:
        self.matrix.set_values([r / 1000.0 for r in sample.r_ohm])

    def on_vital(self, v) -> None:
        self.vital.update_vital(v.hr_bpm, v.rr_bpm, v.quality)

    def on_system_status(self, s) -> None:
        self.vital.update_status(s.level_pct, s.uptime_s)

    def restyle(self) -> None:
        """主题切换时 MainWindow 调用，重新绘制。"""
        from PySide6.QtWidgets import QFrame
        L = theme.current()
        for w in self.findChildren(QFrame):
            if w.objectName() == "Panel":
                w.setStyleSheet(
                    f"#Panel{{background:{L['bg_secondary']};"
                    f"border:1px solid {L['border_default']};"
                    f"border-radius:{theme.RADIUS['md']}px;}}"
                )
        self.ecg.restyle()
        self.piezo.restyle()
        self.matrix.restyle()
        self.scale_bar.restyle()
        self.vital.restyle()
        self.update()