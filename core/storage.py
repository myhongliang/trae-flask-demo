"""存储层：CSV 记录 / 回放 / 列表 / 删除。

CSV 列固定为：
  ts, ecg1, ecg2, ecg3, ecg4, m0..m15, piezo1, piezo2, hr
共 24 列。ts 为相对开始记录的秒数（保留 3 位小数）。
"""

from __future__ import annotations

import csv
import os
import time
from dataclasses import dataclass
from typing import List, Optional

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
)

COLUMNS = (
    ["ts", "ecg1", "ecg2", "ecg3", "ecg4"]
    + [f"m{i}" for i in range(16)]
    + ["piezo1", "piezo2", "hr"]
)


@dataclass
class RecordSession:
    """一次记录会话。"""

    filename: str
    filepath: str
    start_ts: float
    row_count: int = 0
    writer: object = None   # csv.writer
    file: object = None     # 底层文件句柄

    def write(self, ecg: List[float], matrix: List[float], piezo: List[float], hr: int) -> None:
        if self.writer is None:
            return
        ts = round(time.time() - self.start_ts, 3)
        row = [ts] + list(ecg) + list(matrix) + list(piezo) + [hr]
        self.writer.writerow(row)
        self.row_count += 1

    def close(self) -> int:
        if self.file is not None:
            self.file.close()
            self.file = None
            self.writer = None
        return self.row_count


class StorageService:
    def __init__(self, data_dir: str = DATA_DIR) -> None:
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self._current: Optional[RecordSession] = None

    @property
    def is_recording(self) -> bool:
        return self._current is not None

    @property
    def current_filename(self) -> Optional[str]:
        return self._current.filename if self._current else None

    def start(self, name: Optional[str] = None) -> str:
        """开始新记录，返回文件名。如果已在记录则抛错。"""
        if self.is_recording:
            raise RuntimeError("already recording")
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = name if name else f"record_{ts}.csv"
        filepath = os.path.join(self.data_dir, filename)
        f = open(filepath, "w", newline="", encoding="utf-8")
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        self._current = RecordSession(
            filename=filename,
            filepath=filepath,
            start_ts=time.time(),
            writer=writer,
            file=f,
        )
        return filename

    def write(self, ecg, matrix, piezo, hr: int) -> None:
        if self._current is None:
            return
        self._current.write(ecg, matrix, piezo, hr)

    def stop(self) -> Optional[str]:
        """停止记录，返回文件名。"""
        if self._current is None:
            return None
        filename = self._current.filename
        self._current.close()
        self._current = None
        return filename

    def list_records(self) -> List[dict]:
        items = []
        if not os.path.isdir(self.data_dir):
            return items
        for fn in sorted(os.listdir(self.data_dir), reverse=True):
            if not fn.endswith(".csv"):
                continue
            full = os.path.join(self.data_dir, fn)
            try:
                mtime = os.path.getmtime(full)
                size = os.path.getsize(full)
                with open(full, "r", encoding="utf-8") as f:
                    rows = max(sum(1 for _ in f) - 1, 0)
                items.append(
                    {
                        "filename": fn,
                        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                        "size": size,
                        "rows": rows,
                    }
                )
            except Exception:
                continue
        return items

    def read_for_playback(self, filename: str):
        """读取 CSV 用于回放。yield 每一行字典（不含表头）。"""
        if not filename.endswith(".csv"):
            filename += ".csv"
        full = os.path.join(self.data_dir, filename)
        if not os.path.isfile(full):
            raise FileNotFoundError(full)
        with open(full, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row

    def delete(self, filename: str) -> None:
        if not filename.endswith(".csv"):
            filename += ".csv"
        full = os.path.join(self.data_dir, filename)
        if os.path.isfile(full):
            os.remove(full)
