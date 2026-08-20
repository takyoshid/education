"""演習: 「タイムアウトした呼び出しの結果は分からない」を、コードで確認する。

    python3 -m unittest discover -s tests -v

分散システムで最初に受け入れるべき事実を、型と例外で表現します。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, TypeVar

T = TypeVar("T")


class Outcome(Enum):
    """リモート呼び出しの結果は 3 通りある。

    ローカル関数呼び出しには SUCCESS と FAILED しか無い。
    UNKNOWN が現れることが、分散システムの本質的な難しさ。
    """

    SUCCESS = "success"
    FAILED = "failed"      # 相手が明示的に拒否した(=副作用は起きていない)
    UNKNOWN = "unknown"    # 応答が無い(=副作用が起きたか分からない)


class RemoteTimeout(Exception):
    """応答が無かった。処理されたかどうかは分からない。"""


class RemoteRejected(Exception):
    """相手が明示的に拒否した。処理されていないことが確実。"""


@dataclass
class CallResult:
    outcome: Outcome
    value: object = None

    def is_safe_to_retry(self, *, idempotent: bool) -> bool:
        """この結果を受けて再試行してよいか。

        要件:
          - SUCCESS なら再試行しない (False)
          - FAILED なら再試行してよい (True)。副作用は起きていないため
          - UNKNOWN は【冪等な操作のときだけ】再試行してよい

        Phase 8 Lesson 05 の「timeout は失敗ではなく結果不明」の実装。
        """
        raise NotImplementedError


def call_remote(func: Callable[[], T]) -> CallResult:
    """リモート呼び出しをラップし、結果を 3 状態で返す。

    要件:
      - 正常終了 → Outcome.SUCCESS(value に戻り値)
      - RemoteRejected → Outcome.FAILED
      - RemoteTimeout → Outcome.UNKNOWN
      - それ以外の例外はそのまま送出する(握りつぶさない)
    """
    raise NotImplementedError


class UnreliableService:
    """ネットワークの不確実性を模したサービス。

    「処理は成功したが応答が失われた」状況を再現できる。
    """

    def __init__(self) -> None:
        self.applied: list[str] = []   # 実際に適用された副作用の記録

    def submit(self, request_id: str, *, lose_response: bool = False) -> str:
        """リクエストを処理する。lose_response=True なら応答だけが失われる。

        要件:
          - 副作用(self.applied への追記)は必ず先に行う
          - lose_response なら、そのあと RemoteTimeout を送出する
          - そうでなければ "ok" を返す

        これが二将軍問題の再現です。呼び出し側は
        「applied に入ったかどうか」を知る手段がありません。
        """
        raise NotImplementedError

    def submit_idempotent(self, request_id: str, *, lose_response: bool = False) -> str:
        """冪等版。同じ request_id は 1 回しか適用しない。

        要件:
          - すでに applied に含まれる request_id なら、副作用を追加しない
          - それ以外は submit と同じ挙動

        これがあれば、UNKNOWN のときに安全に再試行できる。
        """
        raise NotImplementedError
