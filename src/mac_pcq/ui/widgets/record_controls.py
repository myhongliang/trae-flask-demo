"""RecordControls：录制 / 停止 / 导出（参见《UI 设计》§6.5）。

- 用按钮组件（primary/danger/secondary）
- 40px 高度 / 64px 最小宽度
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout

from .buttons import PrimaryButton, DangerButton, SecondaryButton


class RecordControls(QWidget):
    start_clicked = Signal()
    stop_clicked = Signal()
    export_clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.start_btn = DangerButton("开始录制", icon="record")
        self.start_btn.clicked.connect(self.start_clicked)
        layout.addWidget(self.start_btn)

        self.stop_btn = SecondaryButton("停止", icon="stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_clicked)
        layout.addWidget(self.stop_btn)

        self.export_btn = PrimaryButton("导出 CSV", icon="download")
        self.export_btn.clicked.connect(self.export_clicked)
        layout.addWidget(self.export_btn)

        layout.addStretch(1)

    def set_recording(self, on: bool) -> None:
        self.start_btn.setEnabled(not on)
        self.stop_btn.setEnabled(on)