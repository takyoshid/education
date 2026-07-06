"""
演習 ex03: SOLID原則違反の発見と修正

【目的】
SOLID原則のどれが違反されているかを特定し、修正する練習をする。

【進め方】
1. 各問題の「悪いコード」を読み、どのSOLID原則が違反されているか特定する
2. 違反の内容をコメントに書く
3. 自分でリファクタリングしてみる
4. 解答を確認する (solutions/ex03-solid-violations-solution.py)

【SOLID原則の復習】
S: Single Responsibility Principle (単一責任原則)
O: Open/Closed Principle (開放閉鎖原則)
L: Liskov Substitution Principle (リスコフの置換原則)
I: Interface Segregation Principle (インターフェース分離原則)
D: Dependency Inversion Principle (依存関係逆転原則)

【評価基準】
- 違反しているSOLID原則を正しく特定できているか
- リファクタリング後に元の振る舞いが維持されているか
- 新しい機能を追加するときに既存コードを変更しなくてよい構造になっているか
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

# =============================================================================
# 問題 1: 開放閉鎖原則 (OCP) の違反
# =============================================================================
# このコードはどのSOLID原則に違反しているか?
# 違反している箇所にコメントで「[OCP違反]」と書き、修正すること。
#
# 要件: 将来、給与計算方法に「フリーランス(時給制)」が追加される可能性がある。
# 修正後のコードは、フリーランスを追加する際に EmployeeSalaryCalculator クラスを
# 変更しなくてよい構造にすること。

@dataclass
class Employee:
    name: str
    employee_type: str  # "full_time" | "part_time"
    base_salary: int    # 月給 (正社員) または 時給 (パート)
    hours_worked: int   # 月間労働時間 (パートのみ使用)


class EmployeeSalaryCalculator:
    def calculate(self, employee: Employee) -> int:
        # [? 違反] どの原則の違反か特定してコメントを書くこと
        if employee.employee_type == "full_time":
            return employee.base_salary
        elif employee.employee_type == "part_time":
            return employee.base_salary * employee.hours_worked
        else:
            raise ValueError(f"Unknown employee type: {employee.employee_type}")


# 問題1の動作確認用テスト (変更しないこと)
def test_salary_calculator():
    calc = EmployeeSalaryCalculator()

    full_time = Employee("Alice", "full_time", 300000, 160)
    assert calc.calculate(full_time) == 300000

    part_time = Employee("Bob", "part_time", 1200, 80)
    assert calc.calculate(part_time) == 96000

    print("問題1: OK")


# =============================================================================
# 問題 2: リスコフの置換原則 (LSP) の違反
# =============================================================================
# 以下のコードはどのSOLID原則に違反しているか?
# 違反している箇所を特定し、なぜ問題になるかを説明して修正すること。
#
# ヒント: Bird の fly() を呼ぶコードが、Penguin を渡されたとき壊れないか?

class Bird:
    def fly(self) -> str:
        return "羽ばたいて飛ぶ"

    def eat(self) -> str:
        return "食べる"


class Sparrow(Bird):
    def fly(self) -> str:
        return "素早く飛ぶ"


class Penguin(Bird):
    def fly(self) -> str:
        # [? 違反] どの原則の違反か特定してコメントを書くこと
        raise NotImplementedError("ペンギンは飛べない!")


def make_bird_fly(bird: Bird) -> str:
    """すべての鳥を飛ばす。"""
    return bird.fly()


# 問題2の動作確認用テスト (変更しないこと)
def test_birds():
    sparrow = Sparrow()
    assert make_bird_fly(sparrow) == "素早く飛ぶ"

    # リファクタリング後: Penguin を make_bird_fly に渡してもクラッシュしない構造を実現すること
    # penguin = Penguin()
    # make_bird_fly(penguin)  # これが例外を送出してはいけない

    print("問題2: OK (ただし Penguin のテストを追加すること)")


# =============================================================================
# 問題 3: 依存関係逆転原則 (DIP) の違反
# =============================================================================
# OrderService は具体的な実装クラスに直接依存している。
# 依存関係逆転原則を適用して、抽象(インターフェース)に依存するよう修正すること。
#
# 修正後の要件:
# - テスト時は FakeOrderRepository (DBを使わないインメモリ実装) を使えること
# - 本番時は PostgreSQLOrderRepository を使えること
# - OrderService は具体的な実装を知らなくてよい

class PostgreSQLOrderRepository:
    """PostgreSQL を使った注文の永続化。本番用。"""

    def save(self, order: dict) -> int:
        # 実際には DB に書き込むが、ここでは省略
        print(f"PostgreSQL に保存: {order}")
        return 1  # 生成された order_id

    def find_by_id(self, order_id: int) -> dict | None:
        # 実際には DB から読み込むが、ここでは省略
        return {"id": order_id, "status": "pending"}


class OrderService:
    def __init__(self):
        # [? 違反] どの原則の違反か特定してコメントを書くこと
        self.repository = PostgreSQLOrderRepository()  # 具体実装に直接依存

    def place_order(self, user_id: int, items: list) -> int:
        order = {"user_id": user_id, "items": items, "status": "pending"}
        return self.repository.save(order)

    def get_order(self, order_id: int) -> dict | None:
        return self.repository.find_by_id(order_id)


# 問題3の動作確認用テスト (変更しないこと)
def test_order_service():
    # リファクタリング後: FakeOrderRepository を使ってテストできること
    # service = OrderService(repository=FakeOrderRepository())
    # order_id = service.place_order(user_id=1, items=[{"product_id": "P001", "qty": 2}])
    # assert order_id is not None
    # order = service.get_order(order_id)
    # assert order["status"] == "pending"

    # 現在は直接テストが難しいため、コメントアウトしてある
    print("問題3: リファクタリング後にFakeRepositoryでテストを通すこと")


if __name__ == "__main__":
    test_salary_calculator()
    test_birds()
    test_order_service()
