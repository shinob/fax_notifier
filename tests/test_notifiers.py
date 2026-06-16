from unittest.mock import MagicMock, patch

import pytest

from fax_notifier.config import EmailConfig, SlackConfig
from fax_notifier.notifiers.email_notifier import EmailNotifier
from fax_notifier.notifiers.slack_notifier import SlackNotifier


@pytest.fixture
def dummy_pdf(tmp_path):
    p = tmp_path / "test.pdf"
    p.write_bytes(b"%PDF-1.4 test")
    return str(p)


def test_email_notifier_sends(dummy_pdf):
    cfg = EmailConfig(
        enabled=True,
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="user@example.com",
        smtp_password="pass",
        recipients=["a@b.com"],
    )
    notifier = EmailNotifier(cfg)

    with patch("fax_notifier.notifiers.email_notifier.smtplib.SMTP") as MockSMTP:
        mock_smtp = MagicMock()
        MockSMTP.return_value.__enter__.return_value = mock_smtp
        notifier.send(dummy_pdf, 1)
        mock_smtp.send_message.assert_called_once()


def test_slack_notifier_sends(dummy_pdf):
    cfg = SlackConfig(
        enabled=True,
        bot_token="xoxb-test",
        channel="#general",
    )
    with patch("fax_notifier.notifiers.slack_notifier.WebClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        notifier = SlackNotifier(cfg)
        notifier.send(dummy_pdf, 1)
        mock_client.files_upload_v2.assert_called_once()
