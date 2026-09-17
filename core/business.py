"""业务逻辑层：通道映射 / 滑动滤波 / 电阻↔压力换算 / 心率估计。

这一层是上位机软件的核心：
  - 把采集板送来的 16 路电阻原始值，按可配置的通道映射到 4×4 显示位置；
  - 用电阻-压力方程换算成压力值；
  - 对 ECG / 压电信号做轻量滑动平均滤波；
  - 从 ECG 波形粗略估计心率，供 UI 显示。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Tuple

import math


# ---------- 通道映射 -------------------------------------------------------
@dataclass
class ChannelMap:
    """4×4 矩阵：原始通道索引 -> 显示位置 (row, col)。

    默认按行优先：channel 0 -> (0,0), channel 1 -> (0,1), ... channel 15 -> (3,3)。
    用户可在 UI 互换位置后调用 set_mapping 更新。
    """

    mapping: List[Tuple[int, int]] = field(
        default_factory=lambda: [(i // 4, i % 4) for i in range(16)]
    )

    def set_mapping(self, mapping: List[Tuple[int, int]]) -> None:
        if len(mapping) != 16:
            raise ValueError("mapping must have 16 entries")
        self.mapping = mapping

    def apply(self, raw_16: List[float]) -> List[List[float]]:
        """返回 4×4 二维数组，按显示位置排列。"""
        grid = [[0.0] * 4 for _ in range(4)]
        for ch, (r, c) in enumerate(self.mapping):
            grid[r][c] = raw_16[ch] if ch < len(raw_16) else 0.0
        return grid


# ---------- 电阻 ↔ 压力换算 -----------------------------------------------
@dataclass
class PressureCalib:
    """线性换算：P(kPa) = a * R(kΩ) + b。"""

    a: float = 0.5
    b: float = -10.0

    def to_pressure(self, r: float) -> float:
        return self.a * r + self.b

    def to_resistance(self, p: float) -> float:
        return (p - self.b) / self.a if self.a else 0.0


# ---------- 滑动平均滤波 --------------------------------------------------
class MovingAverage:
    def __init__(self, window: int = 5) -> None:
        self.window = window
        self.buf: Deque[float] = deque(maxlen=window)

    def push(self, x: float) -> float:
        self.buf.append(x)
        return sum(self.buf) / len(self.buf)

    def reset(self) -> None:
        self.buf.clear()


# ---------- 心率估计（基于 R 峰阈值） -------------------------------------
class HeartRateEstimator:
    """简化的 R 峰检测：阈值 + 不应期。

    适合演示与原型阶段；上线时建议换成 Pan-Tompkins。
    """

    def __init__(
        self,
        threshold: float = 0.6,
        refractory_ms: int = 250,
        sample_rate: int = 500,
    ) -> None:
        self.threshold = threshold
        self.refractory = refractory_ms * sample_rate // 1000
        self.sample_rate = sample_rate
        self.last_peak_idx: int = -self.refractory
        self.idx = 0
        self.intervals: Deque[float] = deque(maxlen=8)

    def feed(self, x: float) -> Optional[int]:
        """喂一个采样点，返回更新后的 BPM（无更新返回 None）。"""
        self.idx += 1
        if x >= self.threshold and self.idx - self.last_peak_idx > self.refractory:
            if self.last_peak_idx > 0:
                interval = self.idx - self.last_peak_idx
                self.intervals.append(60.0 * self.sample_rate / interval)
                bpm = int(sum(self.intervals) / len(self.intervals))
                self.last_peak_idx = self.idx
                return max(30, min(220, bpm))
            self.last_peak_idx = self.idx
        return None


# ---------- 业务总管 -------------------------------------------------------
class BusinessService:
    """聚合通道映射 / 滤波 / 压力换算 / 心率，供 app 层调用。"""

    def __init__(self, sample_rate: int = 500) -> None:
        self.sample_rate = sample_rate
        self.channel_map = ChannelMap()
        self.calib = PressureCalib()
        self.ecg_filters = [MovingAverage(3) for _ in range(4)]
        self.piezo_filters = [MovingAverage(3) for _ in range(2)]
        self.hr_estimator = HeartRateEstimator(sample_rate=sample_rate)

    def reset(self) -> None:
        for f in self.ecg_filters:
            f.reset()
        for f in self.piezo_filters:
            f.reset()
        self.hr_estimator = HeartRateEstimator(sample_rate=self.sample_rate)

    def filter_ecg(self, ch: int, x: float) -> float:
        return self.ecg_filters[ch].push(x)

    def filter_piezo(self, ch: int, x: float) -> float:
        return self.piezo_filters[ch].push(x)

    def matrix_to_grid(self, raw_16: List[float]) -> List[List[float]]:
        """原始 16 路电阻 -> 4×4 显示布局（不换算压力，UI 可选择显示模式）。"""
        return self.channel_map.apply(raw_16)

    def matrix_to_pressure_grid(self, raw_16: List[float]) -> List[List[float]]:
        resist_grid = self.channel_map.apply(raw_16)
        return [[self.calib.to_pressure(r) for r in row] for row in resist_grid]

    def estimate_hr(self, x: float) -> Optional[int]:
        return self.hr_estimator.feed(x)
