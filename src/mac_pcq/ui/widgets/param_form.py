"""ParamForm：通用参数表单（参见《UI 设计》§6.7）。

- 字段：int / float / bool / choice / string
- 应用 / 导入 / 导出按钮
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QHBoxLayout, QLineEdit,
)

from .. import theme
from .buttons import PrimaryButton, SecondaryButton


@dataclass
class FieldSpec:
    key: str
    label: str
    kind: str = "int"
    choices: list = field(default_factory=list)
    min: float = 0
    max: float = 1_000_000
    step: float = 1
    unit: str = ""


class ParamForm(QWidget):
    apply_clicked = Signal()
    import_clicked = Signal()
    export_clicked = Signal()

    def __init__(self, fields: List[FieldSpec], parent=None) -> None:
        super().__init__(parent)
        self._fields = {f.key: f for f in fields}
        self._widgets: dict = {}

        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for f in fields:
            if f.kind == "int":
                w = QSpinBox()
                w.setRange(int(f.min), int(f.max))
                w.setSingleStep(int(f.step))
            elif f.kind == "float":
                w = QDoubleSpinBox()
                w.setRange(f.min, f.max)
                w.setSingleStep(f.step)
                w.setDecimals(3)
            elif f.kind == "bool":
                w = QCheckBox()
            elif f.kind == "choice":
                w = QComboBox()
                for label, _ in f.choices:
                    w.addItem(label)
            elif f.kind == "string":
                w = QLineEdit()
            else:
                raise ValueError(f"unknown field kind: {f.kind}")
            self._widgets[f.key] = w
            label = f.label + (f" ({f.unit})" if f.unit else "")
            layout.addRow(label, w)

        row = QHBoxLayout()
        row.setSpacing(8)
        apply_btn = PrimaryButton("应用到设备", icon="upload")
        apply_btn.clicked.connect(self.apply_clicked)
        export_btn = SecondaryButton("导出配置", icon="download")
        export_btn.clicked.connect(self.export_clicked)
        import_btn = SecondaryButton("导入配置", icon="upload")
        import_btn.clicked.connect(self.import_clicked)
        row.addWidget(apply_btn)
        row.addStretch(1)
        row.addWidget(export_btn)
        row.addWidget(import_btn)
        layout.addRow("", _wrap(row))

    def set_values(self, values: dict) -> None:
        for k, v in values.items():
            if k not in self._widgets:
                continue
            w = self._widgets[k]
            f = self._fields[k]
            if f.kind == "int":
                w.setValue(int(v))
            elif f.kind == "float":
                w.setValue(float(v))
            elif f.kind == "bool":
                w.setChecked(bool(v))
            elif f.kind == "choice":
                for i, (_, val) in enumerate(f.choices):
                    if val == v:
                        w.setCurrentIndex(i)
                        break
            elif f.kind == "string":
                w.setText(str(v))

    def get_values(self) -> dict:
        out: dict = {}
        for k, w in self._widgets.items():
            f = self._fields[k]
            if f.kind == "int":
                out[k] = w.value()
            elif f.kind == "float":
                out[k] = w.value()
            elif f.kind == "bool":
                out[k] = w.isChecked()
            elif f.kind == "choice":
                idx = w.currentIndex()
                if 0 <= idx < len(f.choices):
                    out[k] = f.choices[idx][1]
            elif f.kind == "string":
                out[k] = w.text()
        return out


def _wrap(layout) -> QWidget:
    w = QWidget()
    w.setLayout(layout)
    return w