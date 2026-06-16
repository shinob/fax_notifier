# 目的

FAX受信時にメールなどを用いて通知を行いたい

# 概要

複合機で受信したFAXをファイルサーバーやNASに保存するよう設定し、新しいFAXを受信したらFAXのファイルを添付してメールなどで指定した先に通知する。

# 通知可能なシステム

- Eメール
- LINE
- Slack
- Web UI（ブラウザ内でFAX一覧・プレビューを確認）

## 料金について

| サービス | 無料プラン | 制限・注意点 |
|---------|-----------|------------|
| Eメール（Gmail SMTP） | ✅ 無料 | 500通/日まで |
| LINE Messaging API | ⚠️ 条件付き無料 | 200通/月まで無料。超過は従量課金（¥15,000/月〜） |
| Slack | ✅ 無料プランあり | メッセージ履歴90日制限。Bot通知・ファイル添付は無料枠で可能 |
| Microsoft Teams | ✅ 無料プランあり | Microsoft 365契約済みなら追加費用なし |
| Google Chat | ⚠️ 条件付き | Google Workspace（有料）契約が必要 |
| Chatwork | ✅ 無料プランあり | コンタクト数40人・メッセージ履歴に制限 |
| Discord | ✅ 完全無料 | Webhookでファイル添付も無料 |

> FAX受信件数が少ない環境ではほとんどのサービスが無料枠で運用可能。
> LINEは月200通を超えると費用が発生するため、受信件数が多い場合は注意。

# 設定項目

## Eメール

- SMTPサーバー
- ログインID
- ログインパスワード
- 通知先アドレス

## LINE

LINE Messaging API を使用する。

- チャンネルアクセストークン
- チャンネルシークレット
- 送信先ユーザーID / グループID

## Slack

Slack Web API（Bot Token）を使用する。ファイル添付に対応。

- Bot Token（`xoxb-...`）
- 送信先チャンネル名 / チャンネルID

## Web UI

- ポート番号（デフォルト: 5000）
- ポーリング間隔（秒）（デフォルト: 10秒）

# システム構成

- OS: Linux / Windows / macOS（クロスプラットフォーム対応）
- 開発言語: Python 3.11+
- DB: SQLite（通知履歴の管理・重複送信防止・FAX受信履歴の保存に使用）
- Webフレームワーク: Flask（軽量・シンプル、ローカル用途に適切）
- FAXプレビュー: PDF はブラウザネイティブ表示、TIFF は Pillow で PNG 変換

# ソースコード管理

## リポジトリ名

`fax_notifier`

## 更新手順

1. `git pull`
2. `pip install -r requirements.txt`
3. サービスを再起動する
   - Linux（systemd）: `sudo systemctl restart fax-notifier`
   - Windows: タスクスケジューラまたはサービスから再起動
   - macOS: `launchctl unload/load ~/Library/LaunchAgents/fax-notifier.plist`

# 開発ルール

- コーディング規約: PEP 8 準拠
- フォーマッター: Black
- Linter: Ruff
- テスト: pytest
- ブランチ戦略:
  - `main`: リリース済み安定版
  - `feature/*`: 新機能開発
  - `hotfix/*`: 緊急バグ修正

# その他

- FAX監視方式: `watchdog` ライブラリによるディレクトリ監視（ポーリング不要）
- 対応ファイル形式: PDF, TIFF
- 設定ファイル形式: YAML（`config.yaml`）
- ログ管理: Python `logging` モジュールを使用し、ファイルおよび標準出力に出力

## Web UI 仕様

- ブラウザが設定されたポーリング間隔でAPIをポーリングし、新着FAXを検知する
- 新着FAXを検知したら画面上部にバナー通知を表示する
- FAX一覧は受信日時の降順で表示する
- FAX選択時にブラウザ内でプレビューを表示する（PDF: iframe埋め込み、TIFF: PNG変換）
- 認証なし・ローカルLAN内での利用を前提とする
