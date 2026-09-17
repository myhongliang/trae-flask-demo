"""协议层：数据帧解析与配置帧打包。

帧格式（占位实现，便于后续替换为真实采集板协议）:
    STX(0xAA) | LEN(1B) | TYPE(1B) | PAYLOAD(N) | CRC(1B) | ETX(0x55)

帧类型:
    0x01 DATA_FRAME   —— 采集数据（ECG + 压力矩阵 + 压电）
    0x02 CONFIG_FRAME —— 下行配置（采样率 / 通道使能 / 增益）
    0x03 STATUS_FRAME —— 设备状态（连接 / 模块信息）
    0x04 LOG_FRAME    —— 设备日志
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

STX = 0xAA
ETX = 0x55

FRAME_DATA = 0x01
FRAME_CONFIG = 0x02
FRAME_STATUS = 0x03
FRAME_LOG = 0x04


def _crc8(data: bytes) -> int:
    """简单 CRC8（占位，多项式 0x07，初始 0x00）。"""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc << 1) ^ 0x07 if (crc & 0x80) else (crc << 1)
            crc &= 0xFF
    return crc


@dataclass
class Frame:
    type: int
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "payload": self.payload}


def parse_frame(buf: bytes) -> Optional[Frame]:
    """从字节流解析一帧。返回 None 表示数据不完整或校验失败。"""
    if len(buf) < 5 or buf[0] != STX:
        return None
    length = buf[1]
    if len(buf) < length + 5:
        return None
    ftype = buf[2]
    payload_bytes = buf[3 : 3 + length]
    crc = buf[3 + length]
    etx = buf[4 + length]
    if etx != ETX or _crc8(bytes([length, ftype]) + payload_bytes) != crc:
        return None
    try:
        payload = json.loads(payload_bytes.decode("utf-8")) if payload_bytes else {}
    except Exception:
        payload = {"raw": payload_bytes.hex()}
    return Frame(type=ftype, payload=payload)


def pack_frame(ftype: int, payload: Dict[str, Any]) -> bytes:
    """把配置字典打包成字节帧，供下行给采集板。"""
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    length = len(payload_bytes)
    crc = _crc8(bytes([length, ftype]) + payload_bytes)
    return bytes([STX, length, ftype]) + payload_bytes + bytes([crc, ETX])


def pack_config(
    sample_rate: int = 500,
    ecg_channels: int = 4,
    ecg_gain: int = 1,
    matrix_enabled: bool = True,
    piezo_channels: int = 2,
) -> bytes:
    """打包下行配置帧。"""
    return pack_frame(
        FRAME_CONFIG,
        {
            "sample_rate": sample_rate,
            "ecg_channels": ecg_channels,
            "ecg_gain": ecg_gain,
            "matrix_enabled": matrix_enabled,
            "piezo_channels": piezo_channels,
        },
    )


# 便于上层调用 struct 的快捷封装 --------------------------------------------
def pack_data_frame(ecg, matrix, piezo, hr: int = 0) -> bytes:
    """打包上行数据帧（采集板模拟也可用）。"""
    return pack_frame(
        FRAME_DATA,
        {"ecg": list(ecg), "matrix": list(matrix), "piezo": list(piezo), "hr": hr},
    )


def pack_status_frame(status: Dict[str, Any]) -> bytes:
    return pack_frame(FRAME_STATUS, status)


def pack_log_frame(level: str, msg: str) -> bytes:
    return pack_frame(FRAME_LOG, {"level": level, "msg": msg})
