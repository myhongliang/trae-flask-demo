"""新增 / 修订测试。"""

import asyncio
import struct

import pytest

from mac_pcq.protocol.codec import Frame
from mac_pcq.protocol.spec import TYPE_SYS_STATUS
from mac_pcq.transport.adapter import LinkState
from mac_pcq.transport.sim import SimAdapter


@pytest.mark.asyncio
async def test_sim_uptime_is_relative():
    """SimAdapter 应返回自 run() 启动以来的相对秒数，而非绝对时间戳。"""
    sim = SimAdapter(vital_period_s=0.05)
    mgr_cm = []
    sim._info.name = "SimMock"  # placeholder
    await sim.connect()
    sim._boot_time = __import__("time").time() - 100  # 假装启动 100 秒
    # 立即读 status 帧
    raw = sim._encode_status()
    f = Frame.decode(raw)
    assert f.type == TYPE_SYS_STATUS
    seq, flags, level, vbat, v3v3a, v3v3d, temp, uptime, err = struct.unpack_from(
        "<IBBHHHBI B", f.payload, 0
    )
    # uptime 应在 95~110 之间（允许 5s 漂移）
    assert 90 <= uptime <= 110, f"uptime={uptime} not relative to boot"
    await sim.disconnect()


def test_theme_toggle_changes_current():
    from mac_pcq.ui import theme
    # 当前默认可能是 dark 也可能是 light（取决于上一次测试），用相对断言
    start = theme.name()
    new = theme.toggle()
    assert new != start
    assert theme.name() == new
    assert theme.current()["bg_primary"] in ("#F8FAFC", "#0B1120")
    # 再切回
    back = theme.toggle()
    assert back == start
    assert theme.current()["bg_primary"] in ("#F8FAFC", "#0B1120")


def test_theme_subscribe_notified():
    from mac_pcq.ui import theme
    import mac_pcq.ui.theme as theme_mod

    # 清空已有 subscribers
    theme_mod._subscribers.clear()

    # 重置到 dark（避开默认主题，使所有 set_theme 都触发）
    theme_mod._current_theme_name = "dark"

    calls = []
    theme.subscribe(lambda n: calls.append(n))

    # 强制 light → dark → light（顺序确定）
    theme.set_theme("light")
    theme.set_theme("dark")
    theme.set_theme("light")
    assert calls == ["light", "dark", "light"]

    # 重复 set_theme 不通知
    calls.clear()
    theme.set_theme("light")
    assert calls == []

    # 清理
    theme_mod._subscribers.clear()

    # 清理
    theme_mod._subscribers.clear()


def test_pages_import():
    """确保 9 个页面都能 import 并构造。"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from mac_pcq.ui.pages.monitor import PageMonitor
    from mac_pcq.ui.pages.resistive import PageResistive
    from mac_pcq.ui.pages.config import PageConfig
    from mac_pcq.ui.pages.piezo import PagePiezo
    from mac_pcq.ui.pages.vital import PageVital
    from mac_pcq.ui.pages.record import PageRecord
    from mac_pcq.ui.pages.device import PageDevice
    from mac_pcq.ui.pages.upgrade import PageUpgrade
    from mac_pcq.ui.pages.log import PageLog
    for cls in (PageMonitor, PageResistive, PagePiezo, PageVital,
                PageRecord, PageDevice, PageConfig, PageUpgrade, PageLog):
        p = cls()
        assert p is not None


def test_main_window_restyle_no_crash():
    """主题切换不抛异常。"""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from mac_pcq.app import AppController
    from mac_pcq.ui.main_window import MainWindow
    from mac_pcq.ui import theme
    ctrl = AppController()
    win = MainWindow(app_controller=ctrl)
    ctrl.attach_window(win)
    win._toggle_theme()
    win._toggle_theme()
    assert theme.name() == "light"
