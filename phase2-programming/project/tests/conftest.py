"""
conftest.py — pytest の共通設定とフィクスチャ

project/ ディレクトリを sys.path に追加することで、
tests/ サブディレクトリからも models, storage, reports を import できるようにする。
"""

import sys
from pathlib import Path

# project/ ディレクトリを検索パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))
