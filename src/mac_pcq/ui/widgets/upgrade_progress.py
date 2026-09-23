"""UpgradeProgress：升级进度条（参见《UI 设计》§6.8）。

- 6 状态机：idle / checking / upgrading / writing / success / failed
- 进度条 + 状态文字 + 操作按钮
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout

from .. import theme
from .buttons import PrimaryButton, SecondaryButton


class UpgradeProgress(QWidget):
    start_clicked = Signal()
    cancel_clicked = Signal()
    retry_clicked = Signal()

    _STATE = {
        "idle":      ("等待开始",   "text_tertiary"),
        "checking":  ("校验中",     "accent_info"),
        "upgrading": ("升级中",     "accent_info"),
        "writing":   ("写入中",     "accent_info"),
        "success":   ("升级成功",   "accent_success"),
        "failed":    ("升级失败",   "accent_danger"),
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._state_lbl = QLabel("状态：等待开始")
        L = theme.current()
        self._state_lbl.setStyleSheet(
            f"color:{L['text_primary']};font-size:{theme.FONT_SIZE['h3']}px;"
            f"font-weight:{theme.FONT_WEIGHT['semibold']};"
        )
        layout.addWidget(self._state_lbl)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(20)
        layout.addWidget(self._bar)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        self._start_btn = PrimaryButton("开始升级", icon="upgrade", size="md")
        self._start_btn.clicked.connect(self.start_clicked)
        self._cancel_btn = SecondaryButton("取消", size="md")
        self._cancel_btn.clicked.connect(self.cancel_clicked)
        self._retry_btn = SecondaryButton("重试", icon="success", size="md")
        self._retry_btn.clicked.connect(self.retry_clicked)
        self._retry_btn.setVisible(False)
        bar.addWidget(self._start_btn)
        bar.addWidget(self._retry_btn)
        bar.addStretch(1)
        bar.addWidget(self._cancel_btn)
        layout.addLayout(bar)

    def set_progress(self, percent: int, state: str = "upgrading") -> None:
        L = theme.current()
        self._bar.setValue(percent)
        text, color_key = self._STATE.get(state, ("未知", "text_primary"))
        self._state_lbl.setText(f"状态：{text}  {percent}%")
        self._state_lbl.setStyleSheet(
            f"color:{L[color_key]};font-size:{theme.FONT_SIZE['h3']}px;"
            f"font-weight:{theme.FONT_WEIGHT['semibold']};"
        )
        if state == "success":
            self._start_btn.setVisible(False)
            self._retry_btn.setVisible(True)
            self._cancel_btn.setVisible(False)
        elif state == "failed":
            self._start_btn.setVisible(False)
            self._retry_btn.setVisible(True)
            self._cancel_btn.setVisible(True)
        else:
            self._start_btn.setVisible(state == "idle")
            self._retry_btn.setVisible(False)
            self._cancel_btn.setVisible(state != "idle")

    def reset(self) -> None:
        self._bar.setValue(0)
        self.set_progress(0, "idle")