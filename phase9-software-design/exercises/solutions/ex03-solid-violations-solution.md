# 解説 ex03: SOLID原則違反の発見と修正

## 問題1: 開放閉鎖原則 (OCP)

### 違反の特定

```python
class EmployeeSalaryCalculator:
    def calculate(self, employee: Employee) -> int:
        if employee.employee_type == "full_time":
            return employee.base_salary
        elif employee.employee_type == "part_time":
            return employee.base_salary * employee.hours_worked
        else:
            raise ValueError(...)
```

OCP違反のサイン: `if/elif` で型を判定している。
新しい雇用形態を追加するたびに、このクラスを変更しなければならない。

### Strategy パターンの適用

OCP を満たすには「新しい振る舞いを追加するとき、既存コードを変更せず新しいクラスを追加できる」構造にする。

```
EmployeeSalaryCalculator
    ↓ 使う
SalaryStrategy (抽象)
    ↑ 実装
FullTimeSalaryStrategy / PartTimeSalaryStrategy / FreelanceSalaryStrategy
```

フリーランスを追加するとき:
1. `FreelanceSalaryStrategy` を新規作成 ← 追加
2. `EmployeeSalaryCalculator` は変更しない ← 変更なし

これが「拡張に対して開いており、修正に対して閉じている」状態。

### OCPの適用判断

OCPは全ての場合に適用すべきではない。判断基準:

| 適用すべき場面 | 適用不要な場面 |
|-------------|-------------|
| 将来新しい種類が追加されることが明確 | 現在2〜3種類で今後も増えない |
| 分岐が複数箇所に散らばっている | 分岐が1箇所のみ |
| チームが独立して拡張する | 1人が全て管理できる規模 |

---

## 問題2: リスコフの置換原則 (LSP)

### 違反の特定

```python
class Penguin(Bird):
    def fly(self) -> str:
        raise NotImplementedError("ペンギンは飛べない!")
```

LSP違反のサイン: サブクラスのメソッドが例外を送出している。
`Bird` を受け取る関数に `Penguin` を渡すとクラッシュする。

### なぜ問題か

```python
def make_bird_fly(bird: Bird) -> str:
    return bird.fly()  # Penguin を渡すと例外

# 使う側は型を信頼している
birds = [Sparrow(), Penguin()]
for bird in birds:
    make_bird_fly(bird)  # Penguin で落ちる
```

これは「型の契約を破っている」状態。
型ヒントが `Bird` と書いてあるなら、全ての `Bird` サブクラスで正しく動くべき。

### 修正の考え方

「生物学的な分類」ではなく「できること(capability)」で型を設計する:

```
FlyingAnimal (飛べる)
    → Sparrow

SwimmingAnimal (泳げる)
    → Penguin
```

ペンギンを `FlyingAnimal` として扱う必要がなくなるため、LSP問題が発生しない。

### LSP違反のチェック方法

「サブクラスを親クラスの変数に代入して、全てのメソッドを呼んだとき例外なく動くか」を確認する。

```python
bird: Bird = Penguin()
bird.fly()  # ← これが動かなければLSP違反
```

---

## 問題3: 依存関係逆転原則 (DIP)

### 違反の特定

```python
class OrderService:
    def __init__(self):
        self.repository = PostgreSQLOrderRepository()  # 具体クラスに直接依存
```

DIP違反のサイン: コンストラクタ内でクラスをインスタンス化している。
`OrderService` が `PostgreSQLOrderRepository` を直接知っている。

### 依存関係逆転前後の比較

**違反前**:
```
OrderService → PostgreSQLOrderRepository
```
`OrderService` が具体実装を知っている。DB変更時に `OrderService` も変更。

**違反後 (DIP適用)**:
```
OrderService → OrderRepository(抽象) ← PostgreSQLOrderRepository
                                      ← InMemoryOrderRepository
```
`OrderService` は抽象にのみ依存。DB変更時に `OrderService` は変更不要。

### 依存性注入 (Dependency Injection) の3つの方法

```python
# 1. コンストラクタ注入 (推奨)
class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

# 2. メソッド注入 (テスト時に差し替えたい場合)
class OrderService:
    def place_order(self, user_id: int, items: list, repository: OrderRepository) -> int:
        ...

# 3. セッター注入 (あまり推奨しない: 初期化後に未設定のリスク)
class OrderService:
    def set_repository(self, repository: OrderRepository) -> None:
        self._repository = repository
```

コンストラクタ注入が最も推奨される理由:
- インスタンス生成時に依存関係が確定する (未設定のリスクなし)
- 依存関係が明示的 (何が必要かがコンストラクタを見れば分かる)

---

## SOLID原則の適用チェックシート

| 原則 | チェック方法 | 違反のサイン |
|------|------------|------------|
| S (SRP) | 「変更理由はいくつあるか」 | Manager/Helper という名前 |
| O (OCP) | 「新機能追加で既存コードを変えるか」 | if/elif で型を判定している |
| L (LSP) | 「サブクラスを親に代入して全メソッドが動くか」 | サブクラスで NotImplementedError |
| I (ISP) | 「実装したくないメソッドがインターフェースにあるか」 | pass または raise NotImplemented |
| D (DIP) | 「具体クラスをコンストラクタで生成しているか」 | `__init__` 内の `XxxConcreteClass()` |
