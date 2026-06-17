from __future__ import annotations

import logging
import os
import sys
import threading
from typing import List

from .config import load_config
from .database import init_db
from .notifiers.base import BaseNotifier
from .notifiers.email_notifier import EmailNotifier
from .notifiers.line_notifier import LineNotifier
from .notifiers.slack_notifier import SlackNotifier
from .paths import app_data_path
from .watcher import FaxWatcher
from .web.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(app_data_path("fax_notifier.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("FAX_DB_PATH", app_data_path("fax_notifier.db"))
CONFIG_PATH = os.environ.get("FAX_CONFIG_PATH", app_data_path("config.yaml"))


def build_notifiers(config) -> List[BaseNotifier]:
    notifiers: List[BaseNotifier] = []
    n = config.notifications

    if n.email.enabled:
        notifiers.append(EmailNotifier(n.email))
        logger.info("メール通知: 有効")

    if n.line.enabled:
        notifiers.append(LineNotifier(n.line))
        logger.info("LINE通知: 有効")

    if n.slack.enabled:
        notifiers.append(SlackNotifier(n.slack))
        logger.info("Slack通知: 有効")

    return notifiers


def run():
    config = load_config(CONFIG_PATH)
    init_db(DB_PATH)

    notifiers = build_notifiers(config)
    watcher = FaxWatcher(config, notifiers=notifiers, db_path=DB_PATH)
    watcher.start()

    flask_app = create_app(config, db_path=DB_PATH)

    def run_flask():
        flask_app.run(host="0.0.0.0", port=config.web.port, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Web UI 起動: http://localhost:%d", config.web.port)

    try:
        flask_thread.join()
    except KeyboardInterrupt:
        logger.info("終了シグナル受信")
    finally:
        watcher.stop()


if __name__ == "__main__":
    run()
