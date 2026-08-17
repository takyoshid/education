"""演習: replication lag が生む 3 つの異常を再現し、対策する。

    python3 -m unittest discover -s tests -v

leader と follower を模擬し、遅延を自分で進めることで
「たまに起きる」異常を確定的に再現します。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WriteRecord:
    key: str
    value: str
    position: int   # leader 上での書き込み順序(単調増加)


class Leader:
    """書き込みを受け付ける唯一のノード"""

    def __init__(self) -> None:
        self.log: list[WriteRecord] = []
        self.data: dict[str, str] = {}

    def write(self, key: str, value: str) -> int:
        """書き込んで、その書き込み位置(position)を返す。

        要件:
          - position は 1 から始まる単調増加の整数
          - data を更新し、log に WriteRecord を追加する
        """
        raise NotImplementedError

    def read(self, key: str) -> str | None:
        return self.data.get(key)


@dataclass
class Follower:
    """leader から非同期に複製されるノード。

    applied_position までを適用済みとする。
    テストから replicate() を呼んで、任意の地点まで進められる。
    """

    leader: Leader
    name: str = "follower"
    applied_position: int = 0
    data: dict[str, str] = field(default_factory=dict)

    def replicate(self, up_to: int | None = None) -> None:
        """leader のログを up_to まで適用する(None なら全部)。

        要件:
          - applied_position より後のエントリだけを、順番に適用する
          - 適用のたびに applied_position を更新する
          - up_to が applied_position 以下なら何もしない
        """
        raise NotImplementedError

    def read(self, key: str) -> str | None:
        return self.data.get(key)

    @property
    def lag(self) -> int:
        """leader からどれだけ遅れているか(未適用のエントリ数)"""
        return len(self.leader.log) - self.applied_position


class ReadRouter:
    """読み取り先を選ぶ。ここに対策を実装する。"""

    def __init__(self, leader: Leader, followers: list[Follower]) -> None:
        if not followers:
            raise ValueError("follower が空です")
        self.leader = leader
        self.followers = followers
        # user_id -> その利用者が最後に書き込んだ position
        self._last_write: dict[str, int] = {}

    def note_write(self, user_id: str, position: int) -> None:
        """ある利用者が書き込んだ位置を記録する。

        要件: その利用者について、より新しい position だけを保持する
        """
        raise NotImplementedError

    def read_naive(self, key: str, follower_index: int = 0) -> str | None:
        """対策なしの読み取り。指定した follower から読むだけ。"""
        return self.followers[follower_index].read(key)

    def read_your_writes(self, user_id: str, key: str) -> str | None:
        """自分の書き込みが必ず見える読み取り。

        要件:
          - この利用者に記録された書き込み位置に追いついている follower があれば
            そこから読む
          - 無ければ leader から読む
          - 書き込み記録が無い利用者は、follower から読んでよい

        これが read-your-writes 一貫性の最も素直な実装です。
        """
        raise NotImplementedError

    def read_monotonic(self, user_id: str, key: str) -> str | None:
        """時間が巻き戻らない読み取り。

        要件:
          - 同じ user_id は常に同じ follower から読む
          - 振り分けは user_id のハッシュで決定的に決める
            (組み込み hash() ではなく、決定的な方法を使うこと)

        複数 follower にランダムに振り分けると monotonic reads が壊れます。
        """
        raise NotImplementedError
