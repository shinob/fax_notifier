from __future__ import annotations

import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ..config import SlackConfig
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class SlackNotifier(BaseNotifier):
    def __init__(self, config: SlackConfig) -> None:
        self._config = config
        self._client = WebClient(token=config.bot_token)

    def send(self, filepath: str, record_id: int) -> None:
        filename = os.path.basename(filepath)
        try:
            self._client.files_upload_v2(
                channel=self._config.channel,
                file=filepath,
                filename=filename,
                initial_comment=f"FAXを受信しました。\nファイル名: {filename}",
            )
            logger.info("Slack送信完了: %s -> %s", filename, self._config.channel)
        except SlackApiError as e:
            logger.error("Slack送信失敗: %s", e.response["error"])
            raise
