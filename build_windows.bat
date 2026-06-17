@echo off
chcp 65001 > nul
echo fax_notifier Windows ビルドスクリプト
echo.

if not exist venv (
    echo 仮想環境を作成中...
    python -m venv venv
)

echo 依存パッケージをインストール中...
call venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (
    echo パッケージのインストールに失敗しました。
    exit /b 1
)

echo.
echo PyInstaller でビルド中...
call venv\Scripts\pyinstaller fax_notifier.spec --clean
if errorlevel 1 (
    echo ビルドに失敗しました。
    exit /b 1
)

if not exist dist\config.yaml (
    if exist config.yaml (
        copy config.yaml dist\config.yaml > nul
    ) else (
        copy config.yaml.example dist\config.yaml > nul
    )
)

echo.
echo ビルド成功: dist\fax_notifier.exe
echo dist\config.yaml を編集してから dist\fax_notifier.exe を実行してください。
