# fax_notifier

複合機で受信したFAXをメール・LINE・Slack・Web UIで通知するシステムです。

## 機能

- FAX保存フォルダを監視し、新着ファイル（PDF / TIFF）を自動検知
- メール（SMTP）・LINE Messaging API・Slack Web API で通知・ファイル添付
- ブラウザからFAX一覧・プレビューを確認できる Web UI
- SQLite によるFAX受信履歴管理・重複送信防止

## 動作環境

- Python 3.9 以上
- Linux / macOS / Windows（クロスプラットフォーム）

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/shinob/fax_notifier.git
cd fax_notifier

# 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 設定

```bash
cp config.yaml.example config.yaml
```

`config.yaml` を編集します。

```yaml
watch:
  directory: /path/to/fax/folder   # FAXファイルの保存先フォルダ

notifications:
  email:
    enabled: false
    smtp_host: smtp.gmail.com
    smtp_port: 587
    smtp_user: your@gmail.com
    smtp_password: your_app_password
    recipients:
      - notify@example.com

  line:
    enabled: false
    channel_access_token: YOUR_LINE_CHANNEL_ACCESS_TOKEN
    channel_secret: YOUR_LINE_CHANNEL_SECRET
    recipients:
      - U000000000000000000000000000000000  # ユーザーID or グループID

  slack:
    enabled: false
    bot_token: xoxb-YOUR_BOT_TOKEN
    channel: "#general"

web:
  port: 5000           # Web UI のポート番号
  polling_interval: 10 # 新着チェック間隔（秒）
```

### 各通知チャネルの設定方法

#### メール（Gmail）

Gmail を使う場合は「アプリパスワード」を発行してください。  
Google アカウント → セキュリティ → 2段階認証を有効化 → アプリパスワード

#### LINE

1. [LINE Developers](https://developers.line.biz/) でチャンネルを作成
2. Messaging API チャンネルの「チャンネルアクセストークン」と「チャンネルシークレット」を取得
3. 通知先のユーザーIDまたはグループIDを `recipients` に設定

#### Slack

1. [Slack API](https://api.slack.com/apps) でアプリを作成
2. `files:write` と `chat:write` のスコープを付与した Bot Token（`xoxb-...`）を取得
3. アプリを通知先チャンネルに招待

## 起動

```bash
source venv/bin/activate
python -m fax_notifier
```

起動後、ブラウザで `http://localhost:5000` を開くとFAX一覧を確認できます。

> **macOS をお使いの場合:** macOS Monterey 以降は AirPlay Receiver がポート 5000 を使用しています。
> `config.yaml` の `web.port` を `5001` など別のポートに変更してください。

### バックグラウンド実行

**Linux（systemd）**

`/etc/systemd/system/fax-notifier.service` を作成:

```ini
[Unit]
Description=fax-notifier
After=network.target

[Service]
WorkingDirectory=/path/to/fax_notifier
ExecStart=/path/to/fax_notifier/venv/bin/python -m fax_notifier
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now fax-notifier
```

**macOS（launchd）**

`~/Library/LaunchAgents/fax-notifier.plist` を作成し、`launchctl load` で登録してください。

## アップデート

```bash
git pull
pip install -r requirements.txt
# サービスを再起動（Linux の場合）
sudo systemctl restart fax-notifier
```

## 開発

```bash
# テスト実行
python -m pytest tests/ -v

# フォーマット
black fax_notifier/ tests/

# Lint
ruff check fax_notifier/ tests/
```

## ライセンス

MIT
