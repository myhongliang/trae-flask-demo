"""LogPanel：日志表格 + 过滤（参见《UI 设计》§6.9）。"""

from __future__ import annotations

from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel,
)

from .. import theme


_LEVEL_COLOR = {
    "DEBUG": "text_tertiary",
    "INFO":  "text_primary",
    "WARN":  "accent_warning",
    "ERROR": "accent_danger",
}


class LogPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: List[Tuple[str, str, str]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 顶部过滤条
        bar = QHBoxLayout()
        bar.setSpacing(8)
        self._level_filter = QComboBox()
        self._level_filter.addItems(["全部", "DEBUG", "INFO", "WARN", "ERROR"])
        self._level_filter.setMinimumWidth(100)
        self._search = QLineEdit()
        self._search.setPlaceholderText("搜索关键字…")
        self._count_lbl = QLabel("0 条")
        self._count_lbl.setStyleSheet(
            f"color:{theme.current()['text_tertiary']};font-size:{theme.FONT_SIZE['small']}px;"
        )
        bar.addWidget(self._level_filter)
        bar.addWidget(self._search, 1)
        bar.addWidget(self._count_lbl)
        layout.addLayout(bar)

        # 表格
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["时间", "级别", "消息"])
        h = self._table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setDefaultSectionSize(28)
        layout.addWidget(self._table, 1)

        self._level_filter.currentIndexChanged.connect(self._refresh)
        self._search.textChanged.connect(self._refresh)

    def append_log(self, ts: str, level: str, msg: str) -> None:
        self._rows.append((ts, level, msg))
        self._refresh()

    def _refresh(self) -> None:
        level_filter = self._level_filter.currentText()
        keyword = self._search.text().lower().strip()
        rows = [
            (ts, lv, m) for (ts, lv, m) in self._rows
            if (level_filter == "全部" or lv == level_filter)
            and (not keyword or keyword in m.lower() or keyword in lv.lower())
        ]
        self._table.setRowCount(len(rows))
        L = theme.current()
        for r, (ts, lv, m) in enumerate(rows):
            c1 = QTableWidgetItem(ts)
            c2 = QTableWidgetItem(lv)
            c3 = QTableWidgetItem(m)
            color_key = _LEVEL_COLOR.get(lv, "text_primary")
            for item in (c1, c2, c3):
                item.setForeground(QColor(L[color_key]))
            if lv == "ERROR":
                f2 = c2.font()
                f2.setBold(True)
                c2.setFont(f2)
            self._table.setItem(r, 0, c1)
            self._table.setItem(r, 1, c2)
            self._table.setItem(r, 2, c3)
        self._count_lbl.setText(f"{len(rows)} 条")