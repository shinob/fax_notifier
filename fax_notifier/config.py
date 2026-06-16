from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

import yaml


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    recipients: List[str] = field(default_factory=list)


@dataclass
class LineConfig:
    enabled: bool = False
    channel_access_token: str = ""
    channel_secret: str = ""
    recipients: List[str] = field(default_factory=list)


@dataclass
class SlackConfig:
    enabled: bool = False
    bot_token: str = ""
    channel: str = "#general"


@dataclass
class WebConfig:
    port: int = 5000
    polling_interval: int = 10


@dataclass
class NotificationsConfig:
    email: EmailConfig = field(default_factory=EmailConfig)
    line: LineConfig = field(default_factory=LineConfig)
    slack: SlackConfig = field(default_factory=SlackConfig)


@dataclass
class AppConfig:
    watch_directory: str = ""
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)
    web: WebConfig = field(default_factory=WebConfig)


def load_config(path: str = "config.yaml") -> AppConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {path}")

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    watch = raw.get("watch", {})
    notif = raw.get("notifications", {})
    web_raw = raw.get("web", {})

    email_raw = notif.get("email", {})
    line_raw = notif.get("line", {})
    slack_raw = notif.get("slack", {})

    config = AppConfig(
        watch_directory=watch.get("directory", ""),
        notifications=NotificationsConfig(
            email=EmailConfig(
                enabled=email_raw.get("enabled", False),
                smtp_host=email_raw.get("smtp_host", "smtp.gmail.com"),
                smtp_port=email_raw.get("smtp_port", 587),
                smtp_user=email_raw.get("smtp_user", ""),
                smtp_password=email_raw.get("smtp_password", ""),
                recipients=email_raw.get("recipients", []),
            ),
            line=LineConfig(
                enabled=line_raw.get("enabled", False),
                channel_access_token=line_raw.get("channel_access_token", ""),
                channel_secret=line_raw.get("channel_secret", ""),
                recipients=line_raw.get("recipients", []),
            ),
            slack=SlackConfig(
                enabled=slack_raw.get("enabled", False),
                bot_token=slack_raw.get("bot_token", ""),
                channel=slack_raw.get("channel", "#general"),
            ),
        ),
        web=WebConfig(
            port=web_raw.get("port", 5000),
            polling_interval=web_raw.get("polling_interval", 10),
        ),
    )

    if not config.watch_directory:
        raise ValueError("watch.directory が設定されていません")

    return config
