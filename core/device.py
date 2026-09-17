"""设备接口层：采集板连接 / 模拟数据生成 / 设备状态 / 日志。

当前阶段使用模拟数据源生成真实感的 ECG + 压力矩阵 + 压电信号。
后续接入真实硬件时，把 `SimDevice` 换成 `SerialDevice`（pyserial 或 WebSerial 转发）
即可，上层调用接口保持不变。
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import List, Optional

from .protocol import (
    FRAME_DATA,
    FRAME_STATUS,
    FRAME_LOG,
    pack_frame,
)


@dataclass
class DeviceInfo:
    """采集板模块信息。"""

    mcu: str = "STM32F411"
    firmware: str = "1.0.0"
    hw_revision: str = "rev-A"
    link: str = "USB-CDC"          # USB-CDC / BLE
    sample_rate: int = 500
    buffer: int = 64
    voltage: float = 3.30
    temperature: float = 35.0
    connected: bool = True


@dataclass
class LogEntry:
    ts: str
    level: str
    msg: str


class SimDevice:
    """模拟采集板：合成 4 路 ECG + 16 路压力电阻 + 2 路压电。

    ECG 使用两个高斯峰叠加 + 噪声，主峰位于 0.55，副峰位于 0.78；
    矩阵：使用径向高斯分布 + 中心压力，模拟一个按压中心点；
    压电：低频正弦 + 噪声。
    """

    def __init__(self, sample_rate: int = 500) -> None:
        self.sample_rate = sample_rate
        self.info = DeviceInfo()
        self.logs: List[LogEntry] = [
            LogEntry(ts=self._now(), level="INFO", msg="Device powered on"),
            LogEntry(ts=self._now(), level="INFO", msg="Firmware 1.0.0 booted"),
            LogEntry(ts=self._now(), level="INFO", msg="Link: USB-CDC up"),
        ]
        self._t = 0.0
        self._phase = random.random() * math.pi * 2
        self._press_center_r = 1.5
        self._press_center_c = 1.5
        self._press_strength = 5.0

    @staticmethod
    def _now() -> str:
        return time.strftime("%H:%M:%S")

    # ---- 数据生成 ----
    def _ecg_one(self, t: float, ch: int) -> float:
        # 一个完整心跳周期 = 1.0s（60 BPM 基线）
        period = 1.0
        x = (t - 0.05 * ch) % period
        # 主峰
        p1 = math.exp(-((x - 0.15) ** 2) / 0.0015)
        # T 波
        p2 = 0.25 * math.exp(-((x - 0.55) ** 2) / 0.008)
        # 基线漂移
        baseline = 0.05 * math.sin(2 * math.pi * 0.1 * t)
        noise = random.gauss(0, 0.015)
        gain = 1.0 + 0.05 * ch
        return (p1 + p2 + baseline + noise) * gain

    def _matrix_one(self, t: float) -> List[float]:
        # 16 路电阻值（kΩ），按压中心强度随时间变化
        strength = self._press_strength * (0.5 + 0.5 * math.sin(2 * math.pi * 0.2 * t))
        out = []
        for r in range(4):
            for c in range(4):
                d = math.hypot(r - self._press_center_r, c - self._press_center_c)
                base = 30.0
                drop = strength * math.exp(-(d ** 2) / 2.0)
                out.append(base - drop + random.gauss(0, 0.3))
        return out

    def _piezo_one(self, t: float) -> List[float]:
        # 2 路低频压力波动
        return [
            2.0 * math.sin(2 * math.pi * 0.5 * t + 0) + random.gauss(0, 0.1),
            1.5 * math.sin(2 * math.pi * 0.8 * t + 1.0) + random.gauss(0, 0.1),
        ]

    def next_sample(self) -> dict:
        """返回一个采样点字典。"""
        dt = 1.0 / self.sample_rate
        self._t += dt
        return {
            "t": self._t,
            "ecg": [self._ecg_one(self._t, ch) for ch in range(4)],
            "matrix": self._matrix_one(self._t),
            "piezo": self._piezo_one(self._t),
        }

    # ---- 模拟下行日志 ----
    def add_log(self, level: str, msg: str) -> None:
        self.logs.append(LogEntry(ts=self._now(), level=level, msg=msg))
        # 只保留最近 200 条
        self.logs = self.logs[-200:]

    def get_status_bytes(self) -> bytes:
        """打包为状态帧字节流。"""
        return pack_frame(
            FRAME_STATUS,
            {
                "mcu": self.info.mcu,
                "firmware": self.info.firmware,
                "link": self.info.link,
                "sample_rate": self.info.sample_rate,
                "voltage": self.info.voltage,
                "temperature": self.info.temperature,
            },
        )

    def get_logs(self) -> List[dict]:
        return [{"ts": l.ts, "level": l.level, "msg": l.msg} for l in self.logs]


class SerialDevice:
    """预留：未来通过 pyserial / WebSerial 桥接真实采集板。

    接口与 SimDevice 保持一致，上层调用无需修改。
    """

    def __init__(self, port: str, baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate
        self.info = DeviceInfo(link=port, connected=False)
        self.logs: List[LogEntry] = []
        self._ser = None  # 实际使用时 import serial

    def connect(self) -> None:
        raise NotImplementedError("真实串口连接在硬件到位后实现")

    def next_sample(self) -> dict:
        raise NotImplementedError

    def get_status_bytes(self) -> bytes:
        return b""

    def get_logs(self) -> List[dict]:
        return []
