from __future__ import annotations

import logging
import os

from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    MessagingApiBlob,
    PushMessageRequest,
    TextMessage,
)

from ..config import LineConfig
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class LineNotifier(BaseNotifier):
    def __init__(self, config: LineConfig) -> None:
        self._config = config
        cfg = Configuration(access_token=config.channel_access_token)
        self._api_client = ApiClient(cfg)
        self._messaging_api = MessagingApi(self._api_client)
        self._blob_api = MessagingApiBlob(self._api_client)

    def send(self, filepath: str, record_id: int) -> None:
        filename = os.path.basename(filepath)
        text = f"FAXを受信しました。\nファイル名: {filename}"

        for recipient in self._config.recipients:
            self._messaging_api.push_message(
                PushMessageRequest(
                    to=recipient,
                    messages=[TextMessage(text=text)],
                )
            )
            logger.info("LINE送信完了: %s -> %s", filename, recipient)
