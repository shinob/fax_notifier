from __future__ import annotations

from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    @abstractmethod
    def send(self, filepath: str, record_id: int) -> None:
        """FAXファイルを指定先に通知する。"""

    def __call__(self, filepath: str, record_id: int) -> None:
        self.send(filepath, record_id)
