"""统一 Modal Dialog（替代 QMessageBox）。

- 二次确认 / 危险操作 输入确认词
- 阻塞式
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDialogButtonBox, QWidget,
)

from .. import theme


class ConfirmDialog(QDialog):
    """通用确认对话框。"""

    def __init__(
        self,
        title: str,
        message: str,
        *,
        confirm_text: str = "确认",
        cancel_text: str = "取消",
        danger: bool = False,
        require_phrase: Optional[str] = None,   # 危险操作需要输入此短语
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        L = theme.current()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title_lbl = QLabel(title)
        title_font = QFont()
        title_font.setPixelSize(theme.FONT_SIZE["h3"])
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(f"color:{L['text_primary']};")
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"color:{L['text_secondary']};font-size:{theme.FONT_SIZE['body']}px;")
        layout.addWidget(msg_lbl)

        self._phrase_edit: Optional[QLineEdit] = None
        if require_phrase:
            warn = QLabel(f'请输入 "<b>{require_phrase}</b>" 以确认此操作：')
            warn.setStyleSheet(f"color:{L['accent_warning']};font-size:{theme.FONT_SIZE['small']}px;")
            layout.addWidget(warn)
            self._phrase_edit = QLineEdit()
            self._phrase_edit.setPlaceholderText(require_phrase)
            layout.addWidget(self._phrase_edit)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addStretch(1)
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setProperty("variant", "danger" if danger else "primary")
        confirm_btn.clicked.connect(self._on_confirm)
        confirm_btn.setDefault(True)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        layout.addLayout(btn_row)

        self._require_phrase = require_phrase

    def _on_confirm(self) -> None:
        if self._phrase_edit is not None:
            if self._phrase_edit.text() != self._require_phrase:
                from .toast import error as toast_error
                toast_error(f"确认短语不正确，请输入 \"{self._require_phrase}\"")
                return
        self.accept()

    @staticmethod
    def ask(
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        confirm_text: str = "确认",
        cancel_text: str = "取消",
        danger: bool = False,
        require_phrase: Optional[str] = None,
    ) -> bool:
        dlg = ConfirmDialog(
            title, message,
            confirm_text=confirm_text, cancel_text=cancel_text,
            danger=danger, require_phrase=require_phrase, parent=parent,
        )
        return dlg.exec() == QDialog.DialogCode.Accepted