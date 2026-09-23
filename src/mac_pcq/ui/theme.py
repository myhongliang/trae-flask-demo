"""Design Token（v2 — 现代仪表盘风格）。

设计取向（依据用户确认）：
    - 现代仪表盘风格（VS Code / Figma / Linear 一脉）
    - 默认浅色 + 暗色（双主题）
    - 玻璃拟态 / 渐变 / 微动画
    - 通道色与品牌主调保持识别一致

关键 Token（参见《UI 设计》§3）：
    - 颜色 / 字号 / 间距 / 圆角 / 阴影 / 动画 / 字体
"""

from __future__ import annotations

# ---- 通道色（不随主题变，保持识别一致 §3 callout）----
CHANNEL_COLORS = {
    0: "#6366F1",   # ch-1 indigo
    1: "#10B981",   # ch-2 emerald
    2: "#F59E0B",   # ch-3 amber
    3: "#3B82F6",   # ch-4 blue
}

# ---- 浅色主题 ----
LIGHT = {
    # Brand
    "brand_primary": "#6366F1",          # indigo-500
    "brand_primary_hover": "#4F46E5",    # indigo-600
    "brand_primary_pressed": "#4338CA",  # indigo-700
    "brand_primary_disabled": "#C7D2FE", # indigo-200

    # Accent
    "accent_success": "#10B981",         # emerald-500
    "accent_warning": "#F59E0B",         # amber-500
    "accent_danger": "#EF4444",          # red-500
    "accent_info": "#3B82F6",            # blue-500

    # Text（现代灰阶，避免纯黑）
    "text_primary": "#0F172A",           # slate-900
    "text_secondary": "#475569",         # slate-600
    "text_tertiary": "#94A3B8",          # slate-400
    "text_inverse": "#F8FAFC",           # slate-50

    # Background（主背景几乎纯白但加微量色温，仪表盘感）
    "bg_primary": "#F8FAFC",             # slate-50
    "bg_secondary": "#FFFFFF",           # 卡片背景纯白
    "bg_tertiary": "#F1F5F9",            # slate-100
    "bg_hover": "#EEF2FF",               # indigo-50
    "bg_accent": "#F5F3FF",              # violet-50

    # Border
    "border_default": "#E2E8F0",         # slate-200
    "border_strong": "#CBD5E1",          # slate-300
    "border_focus": "#6366F1",           # 与主色一致

    # 阴影（§3.4）
    "shadow_xs": "0 1px 2px rgba(15, 23, 42, 0.04)",
    "shadow_sm": "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)",
    "shadow_md": "0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)",
    "shadow_lg": "0 10px 15px -3px rgba(15, 23, 42, 0.10), 0 4px 6px -4px rgba(15, 23, 42, 0.04)",
    "shadow_xl": "0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.04)",

    # Glass / Overlay
    "glass_tint": "rgba(255, 255, 255, 0.7)",
    "overlay_dim": "rgba(15, 23, 42, 0.4)",

    # 渐变（用于强调按钮 / 顶栏背景）
    "gradient_primary": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #8B5CF6)",
    "gradient_brand_soft": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #3B82F6)",
    "gradient_success": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669)",
    "gradient_danger": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626)",
}

# ---- 深色主题（仪表盘默认 / 第一主题）----
DARK = {
    "brand_primary": "#818CF8",           # indigo-400
    "brand_primary_hover": "#A5B4FC",     # indigo-300
    "brand_primary_pressed": "#6366F1",   # indigo-500
    "brand_primary_disabled": "#3730A3",  # indigo-800

    "accent_success": "#34D399",          # emerald-400
    "accent_warning": "#FBBF24",          # amber-400
    "accent_danger": "#F87171",           # red-400
    "accent_info": "#60A5FA",             # blue-400

    "text_primary": "#F1F5F9",            # slate-100
    "text_secondary": "#CBD5E1",          # slate-300
    "text_tertiary": "#64748B",           # slate-500
    "text_inverse": "#0F172A",            # slate-900

    "bg_primary": "#0B1120",              # 近黑深蓝（仪表盘典型）
    "bg_secondary": "#111827",            # gray-900
    "bg_tertiary": "#1F2937",             # gray-800
    "bg_hover": "#1E293B",                # slate-800
    "bg_accent": "#1E1B4B",               # indigo-950

    "border_default": "#1F2937",          # gray-800
    "border_strong": "#334155",           # slate-700
    "border_focus": "#818CF8",

    "shadow_xs": "0 1px 2px rgba(0, 0, 0, 0.3)",
    "shadow_sm": "0 1px 3px rgba(0, 0, 0, 0.4), 0 1px 2px rgba(0, 0, 0, 0.3)",
    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -4px rgba(0, 0, 0, 0.4)",
    "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.5)",

    "glass_tint": "rgba(17, 24, 39, 0.7)",
    "overlay_dim": "rgba(0, 0, 0, 0.6)",

    "gradient_primary": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #818CF8, stop:1 #C084FC)",
    "gradient_brand_soft": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #818CF8, stop:1 #60A5FA)",
    "gradient_success": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981)",
    "gradient_danger": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #EF4444)",
}

# ---- 字号（§3.2，px / weight / line-height）----
FONT_SIZE = {
    "display": 28,
    "h1": 22,
    "h2": 18,
    "h3": 16,
    "body": 14,
    "small": 12,
    "tiny": 11,
}
FONT_WEIGHT = {
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
}
FONT_LINE = {
    "tight": 1.2,
    "snug": 1.3,
    "normal": 1.5,
    "loose": 1.6,
}

# ---- 间距（§3.3）----
SPACE = {
    1: 4,
    2: 8,
    3: 12,
    4: 16,
    5: 24,
    6: 32,
    7: 48,
    8: 64,
}

# ---- 圆角（§3.4）----
RADIUS = {
    "xs": 2,
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "full": 9999,
}

# ---- 动画时长（§3.4，单位 ms）----
DURATION = {
    "instant": 60,
    "fast": 120,
    "normal": 200,
    "slow": 320,
    "page": 400,
}

# ---- 按钮尺寸（§5.3）----
BUTTON = {
    "height_sm": 32,
    "height_md": 40,
    "height_lg": 48,
    "min_width": 64,
    "padding_x": 16,
}

# ---- 字体栈（§3.5）----
FONT_STACK = {
    "sans": "Inter, 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', system-ui, sans-serif",
    "mono": "'Roboto Mono', 'JetBrains Mono', 'Cascadia Code', Consolas, monospace",
    "cjk": "'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', 'Inter', sans-serif",
}

# ---- 矩阵色阶基色（§6.2.3，6 种）----
COLOR_BASES = {
    "blue_red":   ["#3B82F6", "#6366F1", "#F59E0B", "#EF4444"],
    "blue_green": ["#3B82F6", "#10B981"],
    "purple_yellow": ["#6366F1", "#FACC15"],
    "gray":       ["#F1F5F9", "#0F172A"],
    "rainbow":    ["#8B5CF6", "#3B82F6", "#10B981", "#EAB308", "#EF4444"],
    "thermal":    ["#0F172A", "#7C3AED", "#DC2626", "#FACC15", "#F8FAFC"],
}

# ---- 主题管理 ----
_current_theme_name: str = "light"    # 默认浅色（更友好，符合设计文档）
_subscribers: list = []


def current() -> dict:
    return DARK if _current_theme_name == "dark" else LIGHT


def name() -> str:
    return _current_theme_name


def set_theme(name: str) -> None:
    global _current_theme_name
    if name not in ("light", "dark"):
        return
    if name == _current_theme_name:
        return
    _current_theme_name = name
    for cb in _subscribers:
        try:
            cb(name)
        except Exception:  # noqa: BLE001
            pass


def toggle() -> str:
    new = "light" if _current_theme_name == "dark" else "dark"
    set_theme(new)
    return new


def subscribe(callback) -> None:
    _subscribers.append(callback)