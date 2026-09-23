"""集中式 QSS 加载器。

- apply_global(app)：启动时一次，根据当前主题替换 token 占位符
- restyle(app)：主题切换时调用，重新注入
- 同时返回常用 QSS 片段供 widget 单独使用
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from . import theme

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

_QSS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "resources", "style.qss",
)


def _token_map() -> dict:
    """主题 token → 占位符字符串。"""
    L = theme.current()
    return {
        "FONT_SANS":      _font_family("sans"),
        "FONT_MONO":      _font_family("mono"),
        "FONT_BODY":      str(theme.FONT_SIZE["body"]),
        "FONT_H1":        str(theme.FONT_SIZE["h1"]),
        "FONT_H2":        str(theme.FONT_SIZE["h2"]),
        "FONT_H3":        str(theme.FONT_SIZE["h3"]),
        "FONT_SMALL":     str(theme.FONT_SIZE["small"]),
        "FONT_TINY":      str(theme.FONT_SIZE["tiny"]),
        "WEIGHT_REGULAR": str(theme.FONT_WEIGHT["regular"]),
        "WEIGHT_MEDIUM":  str(theme.FONT_WEIGHT["medium"]),
        "WEIGHT_SEMIBOLD": str(theme.FONT_WEIGHT["semibold"]),
        "WEIGHT_BOLD":    str(theme.FONT_WEIGHT["bold"]),
        "TEXT_PRIMARY":   L["text_primary"],
        "TEXT_SECONDARY": L["text_secondary"],
        "TEXT_TERTIARY":  L["text_tertiary"],
        "TEXT_INVERSE":   L["text_inverse"],
        "BG_PRIMARY":     L["bg_primary"],
        "BG_SECONDARY":   L["bg_secondary"],
        "BG_TERTIARY":    L["bg_tertiary"],
        "BG_HOVER":       L["bg_hover"],
        "BG_ACCENT":      L["bg_accent"],
        "BORDER_DEFAULT": L["border_default"],
        "BORDER_STRONG":  L["border_strong"],
        "BORDER_FOCUS":   L["border_focus"],
        "BRAND_PRIMARY":        L["brand_primary"],
        "BRAND_PRIMARY_HOVER":  L["brand_primary_hover"],
        "BRAND_PRIMARY_PRESSED": L["brand_primary_pressed"],
        "BRAND_PRIMARY_DISABLED": L["brand_primary_disabled"],
        "ACCENT_SUCCESS":  L["accent_success"],
        "ACCENT_WARNING":  L["accent_warning"],
        "ACCENT_DANGER":   L["accent_danger"],
        "ACCENT_INFO":     L["accent_info"],
        "RADIUS_XS":  str(theme.RADIUS["xs"]),
        "RADIUS_SM":  str(theme.RADIUS["sm"]),
        "RADIUS_MD":  str(theme.RADIUS["md"]),
        "RADIUS_LG":  str(theme.RADIUS["lg"]),
        "RADIUS_XL":  str(theme.RADIUS["xl"]),
        "BUTTON_HEIGHT_SM":     str(theme.BUTTON["height_sm"]),
        "BUTTON_HEIGHT_MD":     str(theme.BUTTON["height_md"]),
        "BUTTON_HEIGHT_LG":     str(theme.BUTTON["height_lg"]),
        "BUTTON_MIN_WIDTH":     str(theme.BUTTON["min_width"]),
        "BUTTON_PADDING_X":     str(theme.BUTTON["padding_x"]),
        "GRADIENT_PRIMARY":    L["gradient_primary"],
        "GRADIENT_BRAND_SOFT": L["gradient_brand_soft"],
        "GRADIENT_SUCCESS":    L["gradient_success"],
        "GRADIENT_DANGER":     L["gradient_danger"],
    }


def _font_family(name: str) -> str:
    return theme.FONT_STACK.get(name, "sans-serif")


def _load_template() -> str:
    if not os.path.isfile(_QSS_PATH):
        return ""
    with open(_QSS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def render_qss() -> str:
    """把 style.qss 模板 + 当前主题 token 拼成最终 QSS 字符串。"""
    template = _load_template()
    tokens = _token_map()
    qss = template
    for key, value in tokens.items():
        qss = qss.replace(f"__{key}__", value)
    return qss


def apply_global(app: "QApplication") -> None:
    """启动时一次性注入 QApplication。"""
    app.setStyleSheet(render_qss())


def restyle(app: "QApplication") -> None:
    """主题切换时重新注入。"""
    apply_global(app)