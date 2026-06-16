import os

import pytest
import yaml

from fax_notifier.config import load_config


def _write_config(tmp_path, data: dict) -> str:
    path = os.path.join(tmp_path, "config.yaml")
    with open(path, "w") as f:
        yaml.dump(data, f)
    return path


def test_load_config_minimal(tmp_path):
    path = _write_config(tmp_path, {"watch": {"directory": str(tmp_path)}})
    config = load_config(path)
    assert config.watch_directory == str(tmp_path)
    assert config.web.port == 5000
    assert config.web.polling_interval == 10


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/config.yaml")


def test_load_config_missing_directory(tmp_path):
    path = _write_config(tmp_path, {})
    with pytest.raises(ValueError, match="watch.directory"):
        load_config(path)


def test_load_config_email(tmp_path):
    data = {
        "watch": {"directory": str(tmp_path)},
        "notifications": {
            "email": {
                "enabled": True,
                "smtp_host": "smtp.example.com",
                "smtp_port": 465,
                "smtp_user": "user@example.com",
                "smtp_password": "pass",
                "recipients": ["a@b.com"],
            }
        },
    }
    path = _write_config(tmp_path, data)
    config = load_config(path)
    assert config.notifications.email.enabled is True
    assert config.notifications.email.smtp_port == 465
    assert config.notifications.email.recipients == ["a@b.com"]


def test_load_config_web(tmp_path):
    data = {
        "watch": {"directory": str(tmp_path)},
        "web": {"port": 8080, "polling_interval": 30},
    }
    path = _write_config(tmp_path, data)
    config = load_config(path)
    assert config.web.port == 8080
    assert config.web.polling_interval == 30
