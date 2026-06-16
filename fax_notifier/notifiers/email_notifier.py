from __future__ import annotations

import logging
import mimetypes
import os
import smtplib
from email.message import EmailMessage

from ..config import EmailConfig
from .base import BaseNotifier

logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    def __init__(self, config: EmailConfig) -> None:
        self._config = config

    def send(self, filepath: str, record_id: int) -> None:
        cfg = self._config
        filename = os.path.basename(filepath)

        msg = EmailMessage()
        msg["Subject"] = f"【FAX受信】{filename}"
        msg["From"] = cfg.smtp_user
        msg["To"] = ", ".join(cfg.recipients)
        msg.set_content(f"FAXを受信しました。\nファイル名: {filename}")

        mime_type, _ = mimetypes.guess_type(filepath)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        with open(filepath, "rb") as f:
            msg.add_attachment(
                f.read(), maintype=maintype, subtype=subtype, filename=filename
            )

        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(cfg.smtp_user, cfg.smtp_password)
            smtp.send_message(msg)

        logger.info("メール送信完了: %s -> %s", filename, cfg.recipients)
