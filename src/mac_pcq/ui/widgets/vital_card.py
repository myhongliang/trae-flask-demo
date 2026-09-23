"""VitalCard：心率 / 呼吸率大字卡片（参见《UI 设计》§6.1.4）。

- HR / RR 用 --font-display 28px + Roboto Mono
- 呼吸式动画提示（pulse）
- 卡片背景渐变 + 阴影
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from .. import theme
from .icon import get_pixmap


class VitalCard(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pulse_anim: Optional[QPropertyAnimation] = None
        self._build()
        self._refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # HR 行
        hr_row = QHBoxLayout()
        hr_row.setSpacing(10)
        self._hr_icon_lbl = QLabel()
        self._hr_icon_lbl.setFixedSize(20, 20)
        self._hr_lbl = QLabel("HR")
        self._hr_lbl.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["medium"]))
        hr_row.addWidget(self._hr_icon_lbl)
        hr_row.addWidget(self._hr_lbl)
        hr_row.addStretch(1)
        self._hr_val = QLabel("--")
        self._hr_val.setStyleSheet(self._val_style(theme.FONT_SIZE["display"], theme.FONT_WEIGHT["bold"], "accent_danger"))
        hr_row.addWidget(self._hr_val)
        self._hr_unit = QLabel("bpm")
        self._hr_unit.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["regular"]))
        hr_row.addWidget(self._hr_unit)
        layout.addLayout(hr_row)

        # RR 行
        rr_row = QHBoxLayout()
        rr_row.setSpacing(10)
        self._rr_icon_lbl = QLabel()
        self._rr_icon_lbl.setFixedSize(20, 20)
        self._rr_lbl = QLabel("RR")
        self._rr_lbl.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["medium"]))
        rr_row.addWidget(self._rr_icon_lbl)
        rr_row.addWidget(self._rr_lbl)
        rr_row.addStretch(1)
        self._rr_val = QLabel("--")
        self._rr_val.setStyleSheet(self._val_style(theme.FONT_SIZE["display"], theme.FONT_WEIGHT["bold"], "accent_info"))
        rr_row.addWidget(self._rr_val)
        self._rr_unit = QLabel("bpm")
        self._rr_unit.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["regular"]))
        rr_row.addWidget(self._rr_unit)
        layout.addLayout(rr_row)

        # 质量指示
        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["medium"]))
        layout.addWidget(self._q_lbl)

        # 分隔
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{theme.current()['border_default']};")
        layout.addWidget(sep)

        # 底部
        bot = QHBoxLayout()
        bot.setSpacing(10)
        self._bat_lbl = QLabel("电量 --%")
        self._bat_lbl.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["regular"]))
        self._uptime_lbl = QLabel("运行时长 00:00:00")
        self._uptime_lbl.setStyleSheet(self._lbl_style(theme.FONT_SIZE["small"], theme.FONT_WEIGHT["regular"]))
        bot.addWidget(self._bat_lbl)
        bot.addStretch(1)
        bot.addWidget(self._uptime_lbl)
        layout.addLayout(bot)

        self._build_pulse()

    def _build_pulse(self) -> None:
        self._pulse_anim = QPropertyAnimation(self, b"pulse_opacity")
        self._pulse_anim.setDuration(1200)
        self._pulse_anim.setStartValue(0.6)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.finished.connect(lambda: None)

    def get_pulse_opacity(self) -> float:
        return getattr(self, "_pulse_opacity", 1.0)

    def set_pulse_opacity(self, v: float) -> None:
        self._pulse_opacity = v
        self.update()

    # Qt 元对象系统识别的属性（供 QPropertyAnimation 使用）
    pulse_opacity = Property(float, get_pulse_opacity, set_pulse_opacity)

    def _lbl_style(self, size: int, weight: int, color_key: str = "text_secondary") -> str:
        L = theme.current()
        return (
            f"color:{L[color_key]};font-size:{size}px;font-weight:{weight};"
            f"background:transparent;border:0;"
        )

    def _val_style(self, size: int, weight: int, color_key: str) -> str:
        L = theme.current()
        return (
            f"color:{L[color_key]};font-size:{size}px;font-weight:{weight};"
            f"font-family:{theme.FONT_STACK['mono']};"
            f"background:transparent;border:0;"
        )

    def _refresh(self) -> None:
        # 图标
        hr_pix = self._tinted_icon("heart", "accent_danger")
        rr_pix = self._tinted_icon("waveform", "accent_info")   # 用波形图标代表 RR
        self._hr_icon_lbl.setPixmap(hr_pix)
        self._rr_icon_lbl.setPixmap(rr_pix)

        # 背景渐变
        L = theme.current()
        bg_color = QColor(L["bg_secondary"])
        self.setStyleSheet(
            f"background:{bg_color.name()};"
            f"border:1px solid {L['border_default']};"
            f"border-radius:12px;"
        )

    def _tinted_icon(self, name: str, color_key: str = "accent_info") -> "QPixmap":
        from PySide6.QtGui import QPixmap
        L = theme.current()
        pix = get_pixmap(name, 20)
        colored = QPixmap(pix.size())
        colored.fill(Qt.GlobalColor.transparent)
        p = QPainter(colored)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            p.setBrush(QColor(L[color_key]))
            p.drawPixmap(0, 0, pix)
        finally:
            p.end()
        return colored

    def paintEvent(self, _evt) -> None:
        # 自定义绘制：在背景上叠一层微弱渐变光晕
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        grad = QLinearGradient(0, 0, rect.width(), rect.height())
        L = theme.current()
        c = QColor(L["brand_primary"])
        c.setAlphaF(0.05)
        grad.setColorAt(0, c)
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(rect, QBrush(grad))
        p.end()

    def update_vital(self, hr_bpm: int, rr_bpm: int, quality: int) -> None:
        self._hr_val.setText(str(hr_bpm))
        self._rr_val.setText(str(rr_bpm))
        self._q_lbl.setText(f"● {self._quality_label(quality)}")
        # 启动呼吸式动画
        if self._pulse_anim and self._pulse_anim.state() != QPropertyAnimation.State.Running:
            self._pulse_anim.start()

    def update_status(self, level_pct: int, uptime_s: int) -> None:
        self._bat_lbl.setText(f"电量 {level_pct}%")
        h = uptime_s // 3600
        m = (uptime_s % 3600) // 60
        s = uptime_s % 60
        self._uptime_lbl.setText(f"运行时长 {h:02d}:{m:02d}:{s:02d}")

    def restyle(self) -> None:
        """主题切换：重新计算背景/标签色 + 重画图标。"""
        self._refresh()

    @staticmethod
    def _quality_label(q: int) -> str:
        if q >= 90:
            return "信号质量 良好"
        if q >= 60:
            return "信号质量 一般"
        return "信号质量 差"