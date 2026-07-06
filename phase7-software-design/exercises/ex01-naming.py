"""
演習 ex01: 命名のリファクタリング

【目的】
悪い命名が引き起こす問題を体験し、意図を明確に伝える命名に直す練習をする。

【進め方】
1. 各問題の「悪いコード」を読み、何が問題かをコメントに書く
2. 自分でリファクタリングしてみる
3. 解答を確認する (solutions/ex01-naming-solution.py)

【評価基準】
- 変数・関数・クラスの名前だけを見て意図が理解できるか
- 型ヒントが正しく付いているか
- コードの振る舞いを変えていないか
"""

# =============================================================================
# 問題 1: 関数名・引数名の改善
# =============================================================================
# 以下の関数は正しく動くが、名前が不明瞭すぎる。
# リファクタリングして意図が明確になるようにすること。

def f(l, n):
    r = []
    for x in l:
        if len(x) > n:
            r.append(x)
    return r


# 問題1の使用例 (動作確認用、変更しないこと)
if __name__ == "__main__":
    words = ["cat", "elephant", "dog", "rhinoceros", "ox"]
    result = f(words, 4)
    assert result == ["elephant", "rhinoceros"], f"Expected ['elephant', 'rhinoceros'], got {result}"
    print("問題1: OK")


# =============================================================================
# 問題 2: 真偽値・定数の命名
# =============================================================================
# 以下のコードには2つの問題がある。
# 1. フラグ変数の名前が意味を伝えていない
# 2. マジックナンバーが使われている
# リファクタリングして意図が明確になるようにすること。

def check(u, t):
    if u["p"] and t > 30:
        return True
    return False


# 問題2の使用例 (動作確認用、変更しないこと)
if __name__ == "__main__":
    user1 = {"p": True, "name": "Alice"}
    user2 = {"p": False, "name": "Bob"}
    assert check(user1, 35) is True
    assert check(user1, 25) is False
    assert check(user2, 35) is False
    print("問題2: OK")


# =============================================================================
# 問題 3: クラスとメソッドの命名
# =============================================================================
# 以下のクラスは動くが、名前から何をするクラスか全く分からない。
# クラス名・メソッド名・属性名をリファクタリングすること。
# ヒント: このクラスはECサイトの「買い物かご」を表している。

class Mgr:
    def __init__(self):
        self.d = {}

    def add(self, pid, qty):
        if pid in self.d:
            self.d[pid] += qty
        else:
            self.d[pid] = qty

    def rm(self, pid):
        if pid in self.d:
            del self.d[pid]

    def cnt(self):
        return sum(self.d.values())

    def get(self):
        return dict(self.d)


# 問題3の使用例 (動作確認用、変更しないこと)
if __name__ == "__main__":
    cart = Mgr()
    cart.add("PROD-001", 2)
    cart.add("PROD-002", 1)
    cart.add("PROD-001", 3)  # 既存商品に追加
    assert cart.cnt() == 6
    cart.rm("PROD-002")
    assert cart.cnt() == 5
    assert cart.get() == {"PROD-001": 5}
    print("問題3: OK")


# =============================================================================
# 問題 4: 嘘をつく名前の修正
# =============================================================================
# 以下のコードには「名前と実装が食い違う」問題がある。
# 名前を実装に合わせるか、実装を名前に合わせることで修正すること。
# どちらが適切かを考え、選んだ理由をコメントに書くこと。

import datetime

def get_active_users(users: list) -> list:
    """アクティブなユーザーを返す。"""
    active = []
    for user in users:
        if user["is_active"]:
            # 問題: get_ という名前なのに最終ログイン時刻を更新している
            user["last_seen"] = datetime.datetime.now().isoformat()
            active.append(user)
    return active


# 問題4の使用例 (動作確認用、変更しないこと)
if __name__ == "__main__":
    users = [
        {"id": 1, "is_active": True, "last_seen": None},
        {"id": 2, "is_active": False, "last_seen": None},
        {"id": 3, "is_active": True, "last_seen": None},
    ]
    result = get_active_users(users)
    assert len(result) == 2
    assert all(u["last_seen"] is not None for u in result)
    print("問題4: OK")
