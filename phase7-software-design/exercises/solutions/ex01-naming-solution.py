"""
解答 ex01: 命名のリファクタリング — 模範解答

【構成】
各問題について:
1. 問題点の分析
2. 改善例
3. 改善の解説
"""

# =============================================================================
# 問題 1 解答: 関数名・引数名の改善
# =============================================================================

# --- 問題点の分析 ---
# f(l, n):
#   - 関数名 `f` は何もしない。「filter」なのか「format」なのか「find」なのか不明
#   - 引数 `l` は何のリストか不明
#   - 引数 `n` は何の数値か不明 (閾値? インデックス? 最大値?)
#   - 戻り値 `r` も意味不明
#   - 型ヒントがない

# --- 改善例 ---
def filter_words_longer_than(words: list[str], min_length: int) -> list[str]:
    """指定した文字数より長い単語のリストを返す。

    Args:
        words: フィルタリング対象の単語リスト。
        min_length: この文字数より長い単語のみを返す。

    Returns:
        min_length より長い単語のリスト(元の順序を維持)。
    """
    return [word for word in words if len(word) > min_length]


# --- 改善の解説 ---
# 1. 関数名: 動詞 + 対象 + 条件の形 "filter_words_longer_than"
#    読んだ瞬間に「単語を、ある長さより長いもので絞り込む」と理解できる
# 2. 引数名: `words`(単語のリスト)、`min_length`(最小文字数)
#    `n` より `min_length` の方が何の数値か明確
# 3. リスト内包表記を使うことでループの意図も簡潔に表現できる
# 4. 型ヒントで引数・戻り値の型が自明


# 動作確認
if __name__ == "__main__":
    words = ["cat", "elephant", "dog", "rhinoceros", "ox"]
    result = filter_words_longer_than(words, 4)
    assert result == ["elephant", "rhinoceros"], f"Got: {result}"
    print("問題1: OK")


# =============================================================================
# 問題 2 解答: 真偽値・定数の命名
# =============================================================================

# --- 問題点の分析 ---
# check(u, t):
#   - 関数名 `check` は何をチェックするのか不明
#   - 引数 `u` はユーザーと分かるが、`t` は何? (time? type? threshold?)
#   - `u["p"]` は何? (premium? phone? permission?)
#   - `30` はマジックナンバー。何の30なのか不明

# --- 改善例 ---

# マジックナンバーに名前をつける
PREMIUM_DISCOUNT_MIN_AGE = 30


def is_eligible_for_premium_discount(user: dict, user_age: int) -> bool:
    """プレミアム割引の対象かどうかを判定する。

    プレミアム会員かつ規定年齢以上のユーザーが対象。

    Args:
        user: ユーザー情報の辞書。`is_premium_member` キーを含むこと。
        user_age: ユーザーの年齢。

    Returns:
        割引対象であれば True。
    """
    return user["is_premium_member"] and user_age >= PREMIUM_DISCOUNT_MIN_AGE


# --- 改善の解説 ---
# 1. 関数名: `is_` プレフィックスで真偽値を返すことが明確
#    `check` より `is_eligible_for_premium_discount` の方が一目で意図が分かる
# 2. 引数名: `u` → `user`、`t` → `user_age`
# 3. キー名: `u["p"]` → `user["is_premium_member"]`
#    `p` は何なのかを呼び出し元で調べる必要がなくなる
# 4. 定数: `30` → `PREMIUM_DISCOUNT_MIN_AGE`
#    「なぜ30なのか」はdocstringやADRで説明するとさらに良い


# 動作確認
if __name__ == "__main__":
    user1 = {"is_premium_member": True, "name": "Alice"}
    user2 = {"is_premium_member": False, "name": "Bob"}
    assert is_eligible_for_premium_discount(user1, 35) is True
    assert is_eligible_for_premium_discount(user1, 25) is False
    assert is_eligible_for_premium_discount(user2, 35) is False
    print("問題2: OK")


# =============================================================================
# 問題 3 解答: クラスとメソッドの命名
# =============================================================================

# --- 問題点の分析 ---
# Mgr クラス:
#   - クラス名 `Mgr` は略語。何のManagerか不明
#   - `d` = 辞書? データ? (実体は商品IDと数量のマッピング)
#   - `add(pid, qty)` は何かを追加するのは分かるが何に?
#   - `rm(pid)` は略語。`remove` と書くべき
#   - `cnt()` は数を数えることは分かるが何の数?
#   - `get()` は何を取得するのか不明

# --- 改善例 ---
from dataclasses import dataclass, field


class ShoppingCart:
    """買い物かごを表す。商品の追加・削除・数量管理を行う。"""

    def __init__(self) -> None:
        self._product_quantities: dict[str, int] = {}

    def add_product(self, product_id: str, quantity: int = 1) -> None:
        """商品をカートに追加する。既にある場合は数量を加算する。"""
        if product_id in self._product_quantities:
            self._product_quantities[product_id] += quantity
        else:
            self._product_quantities[product_id] = quantity

    def remove_product(self, product_id: str) -> None:
        """商品をカートから取り除く。存在しない場合は何もしない。"""
        if product_id in self._product_quantities:
            del self._product_quantities[product_id]

    def total_item_count(self) -> int:
        """カート内の商品総数(数量の合計)を返す。"""
        return sum(self._product_quantities.values())

    def get_contents(self) -> dict[str, int]:
        """カートの中身を {product_id: quantity} の辞書で返す。"""
        return dict(self._product_quantities)


# --- 改善の解説 ---
# 1. クラス名: `Mgr` → `ShoppingCart`
#    「買い物かご」という具体的なドメイン概念が名前に現れている
# 2. 属性: `d` → `_product_quantities`
#    「商品IDと数量のマッピング」であることが名前から分かる
#    `_` プレフィックスで「外部から直接変更すべきでない」ことを示す
# 3. メソッド: `add` → `add_product` (何を追加するかが明確)
#    `rm` → `remove_product` (略語を避ける)
#    `cnt` → `total_item_count` (何の合計数かが明確)
#    `get` → `get_contents` (何を取得するかが明確)


# 動作確認
if __name__ == "__main__":
    cart = ShoppingCart()
    cart.add_product("PROD-001", 2)
    cart.add_product("PROD-002", 1)
    cart.add_product("PROD-001", 3)
    assert cart.total_item_count() == 6
    cart.remove_product("PROD-002")
    assert cart.total_item_count() == 5
    assert cart.get_contents() == {"PROD-001": 5}
    print("問題3: OK")


# =============================================================================
# 問題 4 解答: 嘘をつく名前の修正
# =============================================================================

# --- 問題点の分析 ---
# get_active_users:
#   - `get_` という名前は「取得するだけ」という慣習を持つ
#   - しかし実際には `user["last_seen"]` を更新するという副作用がある
#   - これは「嘘をつく名前」の典型例
#
# 2つの修正方針:
#   A) 名前を実装に合わせる: `get_and_update_active_users` など
#   B) 実装を名前に合わせる: 副作用を取り除き、責務を分離する
#
# → 方針Bが推奨される。「取得」と「更新」は別の責務だから。

import datetime


# 方針B: 責務を分離する
def get_active_users(users: list[dict]) -> list[dict]:
    """アクティブなユーザーのリストを返す。副作用なし。"""
    return [user for user in users if user["is_active"]]


def record_last_seen(users: list[dict]) -> None:
    """指定したユーザーリストの最終確認時刻を現在時刻で更新する。"""
    now = datetime.datetime.now().isoformat()
    for user in users:
        user["last_seen"] = now


# 使う側は2つの関数を組み合わせる
def process_active_users(all_users: list[dict]) -> list[dict]:
    """アクティブユーザーを取得し、最終確認時刻を記録する。"""
    active = get_active_users(all_users)
    record_last_seen(active)
    return active


# --- 改善の解説 ---
# 1. 方針Bを選んだ理由:
#    - `get_active_users` を「副作用なし」にすることで単独でテストしやすくなる
#    - 「アクティブユーザーを取得する」と「最終アクセス時刻を記録する」は
#      別々の変更理由を持つ。将来どちらかだけ変えたい場面が来たとき分離されていると便利
#    - 関数を組み合わせる(compose)ことで柔軟性が増す
# 2. 命名の原則: get_ は副作用を持たない。副作用があるなら動詞を使う(record_, update_, set_)

# 動作確認
if __name__ == "__main__":
    users = [
        {"id": 1, "is_active": True, "last_seen": None},
        {"id": 2, "is_active": False, "last_seen": None},
        {"id": 3, "is_active": True, "last_seen": None},
    ]
    result = process_active_users(users)
    assert len(result) == 2
    assert all(u["last_seen"] is not None for u in result)
    assert users[1]["last_seen"] is None  # 非アクティブユーザーは更新されない
    print("問題4: OK")
