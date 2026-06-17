from __future__ import annotations

import os
import sys


def resource_path(*parts: str) -> str:
    """バンドル内リソースの絶対パスを返す（PyInstaller --onefile 対応）。"""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def app_data_path(*parts: str) -> str:
    """exe と同じディレクトリのユーザーファイルの絶対パスを返す。"""
    if hasattr(sys, "frozen"):
        base = os.path.dirname(sys.executable)
    else:
        base = os.getcwd()
    return os.path.join(base, *parts)
