"""
解答 ex03: SOLID原則違反の発見と修正 — 模範解答
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# =============================================================================
# 問題 1 解答: 開放閉鎖原則 (OCP) の違反 → Strategy パターンで修正
# =============================================================================

# --- 問題点の分析 ---
# 違反原則: OCP (Open/Closed Principle)
#
# `EmployeeSalaryCalculator.calculate` は `employee_type` による
# if/elif 分岐を持っている。
# 「フリーランス」を追加するとき、この関数を直接修正しなければならない。
# これは「拡張に対して開いておらず、修正に対して閉じていない」状態。
#
# 開放閉鎖原則: 「モジュールは拡張に対して開いており、修正に対して閉じていること」
# 意味: 新しい機能は「既存コードを変更せず追加できる」べき。


@dataclass
class Employee:
    name: str
    base_salary: int
    hours_worked: int


class SalaryStrategy(ABC):
    """給与計算戦略の抽象基底クラス。"""

    @abstractmethod
    def calculate(self, employee: Employee) -> int:
        """給与を計算して返す。"""
        ...


class FullTimeSalaryStrategy(SalaryStrategy):
    """正社員の給与計算: 月給固定。"""

    def calculate(self, employee: Employee) -> int:
        return employee.base_salary


class PartTimeSalaryStrategy(SalaryStrategy):
    """パートタイムの給与計算: 時給 × 時間。"""

    def calculate(self, employee: Employee) -> int:
        return employee.base_salary * employee.hours_worked


class FreelanceSalaryStrategy(SalaryStrategy):
    """フリーランスの給与計算: 時給 × 時間 (追加のとき既存コードを変更不要)。"""

    def calculate(self, employee: Employee) -> int:
        # フリーランスは消費税分(10%)を上乗せ
        return int(employee.base_salary * employee.hours_worked * 1.1)


class EmployeeSalaryCalculator:
    """給与計算を戦略に委譲する。新しい雇用形態を追加してもこのクラスは変更不要。"""

    def calculate(self, employee: Employee, strategy: SalaryStrategy) -> int:
        return strategy.calculate(employee)


# --- 改善の解説 ---
# 1. `SalaryStrategy` 抽象クラスで「給与計算の契約(interface)」を定義
# 2. 雇用形態ごとに Strategy クラスを作成
# 3. `EmployeeSalaryCalculator` は抽象に依存するため、新しい雇用形態が
#    追加されても変更不要(OCPを満たす)
# 4. フリーランスを追加するときは `FreelanceSalaryStrategy` を追加するだけ


def test_salary_calculator():
    calc = EmployeeSalaryCalculator()

    full_time = Employee("Alice", 300000, 160)
    assert calc.calculate(full_time, FullTimeSalaryStrategy()) == 300000

    part_time = Employee("Bob", 1200, 80)
    assert calc.calculate(part_time, PartTimeSalaryStrategy()) == 96000

    # フリーランス (既存コードを変更せず追加できた)
    freelance = Employee("Carol", 2000, 100)
    assert calc.calculate(freelance, FreelanceSalaryStrategy()) == 220000

    print("問題1: OK")


# =============================================================================
# 問題 2 解答: リスコフの置換原則 (LSP) の違反 → 継承階層の再設計
# =============================================================================

# --- 問題点の分析 ---
# 違反原則: LSP (Liskov Substitution Principle)
#
# `Penguin` は `Bird` を継承しているが、`Bird` の `fly()` メソッドを
# `NotImplementedError` で上書きしている。
# `make_bird_fly(bird: Bird)` に Penguin を渡すと例外が発生する。
#
# リスコフの置換原則: 「サブクラスは、スーパークラスと置き換えられるべき」
# つまり `Bird` を受け取る場所に `Penguin` を渡しても正しく動くべき。
#
# LSP違反のサイン:
# - サブクラスのメソッドが NotImplementedError を送出している
# - サブクラスのメソッドが「何もしない」オーバーライドをしている
# - isinstance(obj, 具体クラス) でチェックしないと正しく動かない


# 修正方針: 継承ではなく、能力(capability)でインターフェースを分ける

class Animal(ABC):
    """全ての動物の共通インターフェース。"""

    @abstractmethod
    def eat(self) -> str:
        ...


class FlyingAnimal(Animal, ABC):
    """飛ぶことができる動物のインターフェース。"""

    @abstractmethod
    def fly(self) -> str:
        ...


class SwimmingAnimal(Animal, ABC):
    """泳ぐことができる動物のインターフェース。"""

    @abstractmethod
    def swim(self) -> str:
        ...


class Sparrow(FlyingAnimal):
    def fly(self) -> str:
        return "素早く飛ぶ"

    def eat(self) -> str:
        return "種を食べる"


class Penguin(SwimmingAnimal):
    """ペンギンは泳げるが飛べない。FlyingAnimal を継承しない。"""

    def swim(self) -> str:
        return "素早く泳ぐ"

    def eat(self) -> str:
        return "魚を食べる"


def make_flying_animal_fly(animal: FlyingAnimal) -> str:
    """飛べる動物を飛ばす。Penguin はこの関数に渡せない(型システムが防ぐ)。"""
    return animal.fly()


# --- 改善の解説 ---
# 1. 「鳥」という生物学的分類ではなく、「飛べる」「泳げる」という
#    能力(capability)でインターフェースを分ける
# 2. Penguin は `FlyingAnimal` を継承しないため、
#    `make_flying_animal_fly` に渡そうとすると型エラーになる
#    (実行前に問題を発見できる)
# 3. これは「継承より合成(Composition over Inheritance)」の考え方とも関連する
#
# トレードオフ:
# - 型階層が複雑になる可能性がある
# - インターフェースを増やすほど設計の理解コストが上がる
# 判断基準: 「このクラスを親クラスと置き換えられるか?」が常に Yes なら継承、
#           そうでない場合は継承を疑う


def test_birds():
    sparrow = Sparrow()
    assert make_flying_animal_fly(sparrow) == "素早く飛ぶ"

    penguin = Penguin()
    assert penguin.swim() == "素早く泳ぐ"
    # make_flying_animal_fly(penguin) は型エラーになる(意図通り)

    print("問題2: OK")


# =============================================================================
# 問題 3 解答: 依存関係逆転原則 (DIP) の違反 → 依存の注入
# =============================================================================

# --- 問題点の分析 ---
# 違反原則: DIP (Dependency Inversion Principle)
#
# `OrderService` が `PostgreSQLOrderRepository` (具体クラス) に直接依存している。
# 結果として:
# - テスト時に PostgreSQL が必要になる (テストが遅く、環境構築が複雑になる)
# - 将来 DB を変えるとき `OrderService` のコードを変更しなければならない
#
# DIPの原則:
# - 高レベルモジュール (OrderService) は低レベルモジュール (PostgreSQLOrderRepository) に
#   依存すべきでない
# - 両者は抽象 (インターフェース) に依存すべき


class OrderRepository(ABC):
    """注文の永続化の抽象インターフェース。"""

    @abstractmethod
    def save(self, order: dict) -> int:
        """注文を保存し、生成されたorder_idを返す。"""
        ...

    @abstractmethod
    def find_by_id(self, order_id: int) -> dict | None:
        """order_id で注文を検索する。見つからない場合は None を返す。"""
        ...


class PostgreSQLOrderRepository(OrderRepository):
    """PostgreSQL を使った注文の永続化。本番用。"""

    def save(self, order: dict) -> int:
        print(f"PostgreSQL に保存: {order}")
        return 1

    def find_by_id(self, order_id: int) -> dict | None:
        return {"id": order_id, "status": "pending"}


class InMemoryOrderRepository(OrderRepository):
    """メモリを使った注文の永続化。テスト用。DB不要。"""

    def __init__(self) -> None:
        self._orders: dict[int, dict] = {}
        self._next_id = 1

    def save(self, order: dict) -> int:
        order_id = self._next_id
        self._orders[order_id] = {**order, "id": order_id}
        self._next_id += 1
        return order_id

    def find_by_id(self, order_id: int) -> dict | None:
        return self._orders.get(order_id)


class OrderService:
    """注文の配置を担当する。具体的なDB実装には依存しない。"""

    def __init__(self, repository: OrderRepository) -> None:
        # 抽象インターフェースに依存 (コンストラクタ注入)
        self._repository = repository

    def place_order(self, user_id: int, items: list) -> int:
        order = {"user_id": user_id, "items": items, "status": "pending"}
        return self._repository.save(order)

    def get_order(self, order_id: int) -> dict | None:
        return self._repository.find_by_id(order_id)


# --- 改善の解説 ---
# 1. `OrderRepository` 抽象クラスで「保存・取得の契約」を定義
# 2. `OrderService` はコンストラクタで `OrderRepository` (抽象) を受け取る
#    → これを「依存性注入 (Dependency Injection)」と呼ぶ
# 3. テスト時は `InMemoryOrderRepository` を渡す → DB不要、テストが速い
# 4. 本番時は `PostgreSQLOrderRepository` を渡す
# 5. `OrderService` のコードはどちらの場合も変更不要
#
# トレードオフ:
# - 抽象クラスを導入するため、ファイル数が増える
# - コンストラクタに引数が増える
# 判断基準: テストしたいロジックが外部依存を持つなら DIP の適用を検討する


def test_order_service():
    # テスト: InMemoryOrderRepository を使う (DB不要)
    fake_repo = InMemoryOrderRepository()
    service = OrderService(repository=fake_repo)

    order_id = service.place_order(
        user_id=1,
        items=[{"product_id": "P001", "qty": 2}],
    )
    assert order_id is not None
    assert isinstance(order_id, int)

    order = service.get_order(order_id)
    assert order is not None
    assert order["status"] == "pending"
    assert order["user_id"] == 1

    # 存在しない注文
    assert service.get_order(9999) is None

    print("問題3: OK")


if __name__ == "__main__":
    test_salary_calculator()
    test_birds()
    test_order_service()
