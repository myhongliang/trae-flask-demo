"""图标生成脚本（手工一次，重写一次后即固定）。

不依赖任何外部资源，全部 inline SVG 字符串。
颜色用 currentColor（让 Qt QSS 控制前景色）。
"""

from __future__ import annotations

import os

OUT = os.path.dirname(os.path.abspath(__file__))


ICONS = {
    # === 录制/播放控制 ===
    "record": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="currentColor"/></svg>',
    "stop": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><rect x="3" y="3" width="10" height="10" rx="1" fill="currentColor"/></svg>',
    "play": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path d="M5 3 L13 8 L5 13 Z" fill="currentColor"/></svg>',
    "pause": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><rect x="3" y="3" width="3.5" height="10" rx="1" fill="currentColor"/><rect x="9.5" y="3" width="3.5" height="10" rx="1" fill="currentColor"/></svg>',
    "forward": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path d="M3 3 L10 8 L3 13 Z" fill="currentColor"/><rect x="11" y="3" width="2.5" height="10" fill="currentColor"/></svg>',
    "rewind": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><rect x="2.5" y="3" width="2.5" height="10" fill="currentColor"/><path d="M13 3 L6 8 L13 13 Z" fill="currentColor"/></svg>',

    # === 文件/导入/导出 ===
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2 L8 11 M4 8 L8 12 L12 8 M2 14 L14 14"/></svg>',
    "upload": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 14 L8 4 M4 8 L8 4 L12 8 M2 2 L14 2"/></svg>',

    # === 系统 ===
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="2"/><path d="M8 1 L8 3 M8 13 L8 15 M1 8 L3 8 M13 8 L15 8 M3.05 3.05 L4.46 4.46 M11.54 11.54 L12.95 12.95 M3.05 12.95 L4.46 11.54 M11.54 4.46 L12.95 3.05"/></svg>',
    "help": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><path d="M6 6 a2 2 0 1 1 2 2 v2 M8 12.5 L8 13"/></svg>',
    "warning": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2 L14.5 13.5 L1.5 13.5 Z"/><line x1="8" y1="6" x2="8" y2="9.5"/><circle cx="8" cy="11.5" r="0.5" fill="currentColor"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><circle cx="8" cy="5.5" r="0.5" fill="currentColor"/><line x1="8" y1="8" x2="8" y2="11.5"/></svg>',
    "success": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><path d="M5 8 L7 10 L11 6"/></svg>',
    "error": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><line x1="5.5" y1="5.5" x2="10.5" y2="10.5"/><line x1="10.5" y1="5.5" x2="5.5" y2="10.5"/></svg>',

    # === 主题 ===
    "sun": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="3" fill="currentColor"/><path d="M8 1 L8 3 M8 13 L8 15 M1 8 L3 8 M13 8 L15 8 M3.05 3.05 L4.46 4.46 M11.54 11.54 L12.95 12.95 M3.05 12.95 L4.46 11.54 M11.54 4.46 L12.95 3.05"/></svg>',
    "moon": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M13 9.5 A5.5 5.5 0 0 1 6.5 3 A6 6 0 1 0 13 9.5 Z"/></svg>',
    "theme_auto": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="6"/><path d="M8 2 A6 6 0 0 0 8 14 Z" fill="currentColor"/></svg>',

    # === 通讯 ===
    "usb": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="11" r="1.5"/><circle cx="11" cy="11" r="1.5"/><line x1="5" y1="6" x2="5" y2="9.5"/><line x1="11" y1="6" x2="11" y2="9.5"/><polyline points="7,3 9,5 7,7"/></svg>',
    "ble": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M5 2 L11 8 L5 14 L5 9 L9 8 L5 7 Z"/></svg>',
    "link": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M6 10 L10 6 M5 11 L3 9 A2.5 2.5 0 0 1 3 7.5 M11 5 L13 7 A2.5 2.5 0 0 1 13 8.5"/></svg>',
    "link_off": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M6 10 L10 6"/><path d="M5 11 L3 9 A2.5 2.5 0 0 1 3 7.5"/><path d="M11 5 L13 7 A2.5 2.5 0 0 1 13 8.5"/><line x1="2" y1="2" x2="14" y2="14"/></svg>',

    # === 状态 ===
    "battery": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="10" height="6" rx="1"/><line x1="13" y1="7" x2="13" y2="9"/><rect x="3.5" y="6.5" width="6" height="3" fill="currentColor"/></svg>',
    "wifi": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6 A10 10 0 0 1 14 6"/><path d="M4 8.5 A6 6 0 0 1 12 8.5"/><path d="M6.5 11 A2 2 0 0 1 9.5 11"/><circle cx="8" cy="13" r="0.8" fill="currentColor"/></svg>',
    "temperature": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2 A1.5 1.5 0 0 1 9.5 3.5 V10 A2.5 2.5 0 1 1 6.5 10 V3.5 A1.5 1.5 0 0 1 8 2 Z"/><line x1="8" y1="6" x2="8" y2="10.5"/></svg>',

    # === 页面图标 ===
    "monitor": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="12" height="8" rx="1"/><polyline points="5,13 11,13"/><polyline points="8,11 8,13"/></svg>',
    "matrix": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="5" height="5" rx="0.5"/><rect x="9" y="2" width="5" height="5" rx="0.5"/><rect x="2" y="9" width="5" height="5" rx="0.5"/><rect x="9" y="9" width="5" height="5" rx="0.5"/></svg>',
    "waveform": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="2,8 4,8 5,4 6,12 7,6 8,10 9,8 11,8 12,5 13,11 14,8"/></svg>',
    "heart": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 13.5 L1.5 7 A3.5 3.5 0 0 1 6.5 4 L8 5.5 L9.5 4 A3.5 3.5 0 0 1 14.5 7 Z"/></svg>',
    "log": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="4" x2="13" y2="4"/><line x1="3" y1="8" x2="13" y2="8"/><line x1="3" y1="12" x2="9" y2="12"/></svg>',
    "device": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="12" height="9" rx="1"/><line x1="5" y1="13" x2="5" y2="14"/><line x1="11" y1="13" x2="11" y2="14"/><line x1="5" y1="7" x2="9" y2="7"/></svg>',
    "config": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="2"/><path d="M8 1 L8 3 M8 13 L8 15 M2 8 L4 8 M12 8 L14 8 M3.5 3.5 L5 5 M11 11 L12.5 12.5 M3.5 12.5 L5 11 M11 5 L12.5 3.5"/></svg>',
    "upgrade": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 12 L8 3"/><polyline points="5,6 8,3 11,6"/><path d="M2 13 L14 13"/></svg>',

    # === 工具 ===
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="7" cy="7" r="4"/><line x1="10" y1="10" x2="13" y2="13"/></svg>',
    "close": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg>',
    "chevron_right": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><polyline points="4,2 8,6 4,10"/></svg>',
    "chevron_down": '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><polyline points="2,4 6,8 10,4"/></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><line x1="8" y1="3" x2="8" y2="13"/><line x1="3" y1="8" x2="13" y2="8"/></svg>',
    "minimize": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><line x1="3" y1="10" x2="13" y2="10"/></svg>',

    # === App logo ===
    "logo": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6366F1"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs><rect x="2" y="2" width="16" height="16" rx="4" fill="url(#g)"/><polyline points="5,10 8,13 15,7" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}


def main() -> None:
    for name, svg in ICONS.items():
        path = os.path.join(OUT, f"{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"Generated {len(ICONS)} icons in {OUT}")


if __name__ == "__main__":
    main()