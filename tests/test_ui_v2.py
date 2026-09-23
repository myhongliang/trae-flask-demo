"""UI v2 新组件测试（icons / stylesheet / toast / buttons / main_window）。"""

import os


def test_icons_exist():
    """所有 39 个 SVG 必须存在。"""
    icons_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "mac_pcq", "ui", "resources", "icons",
    )
    files = [f[:-4] for f in os.listdir(icons_dir) if f.endswith(".svg")]
    expected = [
        "record", "stop", "play", "pause", "forward", "rewind",
        "download", "upload",
        "settings", "help", "warning", "info", "success", "error",
        "sun", "moon", "theme_auto",
        "usb", "ble", "link", "link_off",
        "battery", "wifi", "temperature",
        "monitor", "matrix", "waveform", "heart", "log", "device", "config", "upgrade",
        "search", "close", "chevron_right", "chevron_down", "plus", "minimize",
        "logo",
    ]
    missing = set(expected) - set(files)
    assert not missing, f"missing icons: {missing}"
    extra = set(files) - set(expected)
    assert not extra, f"unexpected icons: {extra}"


def test_stylesheet_renders():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from mac_pcq.ui.stylesheet import render_qss
    qss = render_qss()
    # 必须替换所有占位符
    assert "__TEXT_PRIMARY__" not in qss
    assert "__BRAND_PRIMARY__" not in qss
    assert "__FONT_BODY__" not in qss
    # 必须包含关键 widget 规则
    assert "QMainWindow" in qss
    assert "QPushButton" in qss
    assert "variant=\"primary\"" in qss


def test_toast_manager():
    """Toast 模块可导入且不会在没有 QApplication 时崩。"""
    from mac_pcq.ui.widgets import toast
    assert hasattr(toast, "success")
    assert hasattr(toast, "error")
    assert hasattr(toast, "warning")
    assert hasattr(toast, "info")
    assert hasattr(toast, "show_toast")


def test_modal_dialog_ask_signature():
    from mac_pcq.ui.widgets.modal import ConfirmDialog
    import inspect
    sig = inspect.signature(ConfirmDialog.ask)
    params = list(sig.parameters.keys())
    # 至少有 title, message, parent
    assert "title" in params
    assert "message" in params


def test_buttons_have_variants():
    from mac_pcq.ui.widgets.buttons import (
        PrimaryButton, SecondaryButton, DangerButton, GhostButton, IconButton,
    )
    assert hasattr(PrimaryButton, "__init__")
    assert hasattr(DangerButton, "__init__")


def test_main_window_navigation():
    """MainWindow 可构造且 9 个页面都有。"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from mac_pcq.app import AppController
    from mac_pcq.ui.main_window import MainWindow
    ctrl = AppController()
    win = MainWindow(app_controller=ctrl)
    ctrl.attach_window(win)
    assert len(win.pages) == 9
    assert len(_nav_names()) == 9
    # 切换页面
    win.goto(3)
    assert win.stack.currentIndex() == 3
    win.goto(7)
    assert win.stack.currentIndex() == 7


def _nav_names():
    from mac_pcq.ui.main_window import _NAV
    return [n for (n, _ic, _c) in _NAV]


def test_main_window_shortcuts_installed():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from mac_pcq.app import AppController
    from mac_pcq.ui.main_window import MainWindow
    ctrl = AppController()
    win = MainWindow(app_controller=ctrl)
    # actions 应当 ≥ 9（1~9 + Ctrl+O/S/E/F1/F5/Esc）
    assert len(win.actions()) >= 9


def test_pages_have_restyle():
    """每个页面要么有 restyle，要么是 StubPage（继承自 _stub 会有 restyle）。"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from mac_pcq.app import AppController
    from mac_pcq.ui.main_window import MainWindow
    ctrl = AppController()
    win = MainWindow(app_controller=ctrl)
    ctrl.attach_window(win)
    for p in win.pages:
        # 应该都有 restyle 方法（StubPage / Monitor / Resistive / Config 都已经实现）
        assert hasattr(p, "restyle"), f"{type(p).__name__} missing restyle()"