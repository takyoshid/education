"""依存関係スケジューラー。"""

from __future__ import annotations

from collections.abc import Iterable


class DependencyError(ValueError):
    pass


def schedule(tasks: Iterable[str], dependencies: Iterable[tuple[str, str]]) -> list[str]:
    """実行順を返す。

    dependenciesの各要素は(task, prerequisite)。複数候補は辞書順で選ぶ。
    """
    raise NotImplementedError
