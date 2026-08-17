# 解説 ex05: テストを書く

## テストケースの選び方

テストは「書けるだけ書く」ではなく、「何をテストすべきか」を考えて選ぶ。

### 正常系・異常系・境界値の3分類

| 分類 | 意味 | 例(ShoppingCart) |
|------|------|----------------|
| 正常系 | 意図した通りに動くケース | 商品を追加して合計が正しい |
| 異常系 | エラーになるべきケース | 数量0を追加したとき ValueError |
| 境界値 | 条件が切り替わる境目 | 数量1(最小有効値)と数量0(最小無効値) |

---

## ShoppingCart のテスト設計

### 見落としやすいケース

1. **空のカートの初期状態**: `get_total()` が 0 を返すか
2. **同じ商品の重複追加**: 新しい CartItem を作るのか、数量を加算するのか
3. **存在しない商品の削除**: 例外を送出するか、何もしないか
4. **単価0円の商品**: `get_total()` が正しく 0 になるか

### テストクラスと `setup_method`

```python
class TestShoppingCart:
    def setup_method(self):
        self.cart = ShoppingCart()  # 各テスト前に新しいカートを作る
```

`setup_method` を使うとテスト間の状態が混在しない。
ただし今回の `ShoppingCart` はステートフル(状態を持つ)なので、
毎回新しいインスタンスを作ることが重要。

---

## PasswordValidator のテスト設計

### 境界値テストの重要性

「8文字以上」というルールをテストするとき、7・8・9文字の3つをテストする:

```
7文字: 失敗 (境界の外)
8文字: 成功 (境界ちょうど)
9文字: 成功 (境界の内側)
```

なぜ3つ必要か:
- `len(password) < 8` と `len(password) <= 8` を書き間違えたとき、
  7文字と9文字だけのテストでは検出できない
- 8文字のテストが「境界ちょうど」のバグを発見する

### 複数エラーのテスト

```python
def test_multiple_violations_returns_all_errors(self):
    result = self.validator.validate("weak")
    assert len(result.errors) == 3  # 短い + 大文字なし + 数字なし
```

1つエラーがあったら即時 return する実装だと、このテストが失敗する。
「全てのエラーを収集して返す」仕様を確認できる。

---

## PriceCalculator の設計改善

### テストできない設計の問題

元のコード:
```python
class PriceCalculator:
    def calculate(self, base_price: int) -> int:
        today = datetime.date.today()  # テストで制御できない
```

「今日が土曜日かどうか」はテストを実行するタイミングによって変わる。
これは「非決定的なテスト(flaky test)」になる。

非決定的なテストの問題:
- CI で毎週土曜だけ失敗する
- 「テストが失敗した = バグがある」という信頼性が失われる

### 依存関係の注入で解決

```python
class DateProvider(ABC):
    def today(self) -> datetime.date: ...

class FixedDateProvider(DateProvider):
    def __init__(self, fixed_date): ...
    def today(self): return self._date

class PriceCalculator:
    def __init__(self, date_provider: DateProvider = None):
        self._provider = date_provider or SystemDateProvider()
```

テスト時は `FixedDateProvider(月曜日)` を渡すことで、
曜日を固定してテストが書ける。

これは「テスタビリティのための設計(design for testability)」の典型パターン。

### 一般化: 外部依存を注入する

テストしにくい外部依存:

| 依存 | テスト用の代替 |
|------|-------------|
| `datetime.date.today()` | `DateProvider` を注入 |
| `random.random()` | `RandomProvider` を注入 |
| `open(file)` | ファイルパスを注入、または `io.StringIO` を使う |
| HTTP APIリクエスト | `requests` をモックに差し替える |
| DBへのクエリ | インメモリ実装を注入 |

---

## テストの品質チェックリスト

- [ ] テスト名が「何をテストしているか」を説明している
- [ ] AAA (Arrange-Act-Assert) の3段階が明確に分かれている
- [ ] 正常系だけでなく異常系もある
- [ ] 境界値を意識してテストしている
- [ ] テストが互いに独立している(実行順序に依存しない)
- [ ] テストが決定的である(実行タイミングによって結果が変わらない)
- [ ] モック/スタブを使いすぎていない(実際の振る舞いをテストしているか)
