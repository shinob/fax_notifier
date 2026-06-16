from __future__ import annotations

import logging
import os
from typing import Callable, List, Optional

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .config import AppConfig
from .database import insert_fax, mark_notified

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".tiff", ".tif"}


class FaxEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        notifiers: List[Callable[[str, int], None]],
        db_path: str = "fax_notifier.db",
    ) -> None:
        self._notifiers = notifiers
        self._db_path = db_path

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        filepath = event.src_path
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return

        logger.info("新着FAX検知: %s", filepath)
        record_id = insert_fax(filepath, db_path=self._db_path)
        if record_id is None:
            logger.debug("重複ファイルのためスキップ: %s", filepath)
            return

        for notifier in self._notifiers:
            try:
                notifier(filepath, record_id)
            except Exception:
                logger.exception("通知失敗: %s", notifier)

        mark_notified(record_id, db_path=self._db_path)


class FaxWatcher:
    def __init__(
        self,
        config: AppConfig,
        notifiers: Optional[List[Callable[[str, int], None]]] = None,
        db_path: str = "fax_notifier.db",
    ) -> None:
        self._config = config
        self._notifiers = notifiers or []
        self._db_path = db_path
        self._observer: Optional[Observer] = None

    def start(self) -> None:
        watch_dir = self._config.watch_directory
        if not os.path.isdir(watch_dir):
            raise NotADirectoryError(f"監視ディレクトリが存在しません: {watch_dir}")

        handler = FaxEventHandler(self._notifiers, db_path=self._db_path)
        self._observer = Observer()
        self._observer.schedule(handler, watch_dir, recursive=False)
        self._observer.start()
        logger.info("FAX監視開始: %s", watch_dir)

    def stop(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("FAX監視停止")
