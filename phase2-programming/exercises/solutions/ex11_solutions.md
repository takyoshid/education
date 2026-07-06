# 演習 11 解説: テストとデバッグ

## テストの命名規則

pytest はファイル名・クラス名・関数名のパターンでテストを自動検出します:

- ファイル: `test_*.py` または `*_test.py`
- クラス: `Test*`
- 関数: `test_*`

テスト名は「何をテストしているか」が一目でわかるように書きましょう:

```
# 悪い例
def test_1():
def test_function():

# 良い例
def test_deposit_increases_balance():
def test_withdraw_raises_when_insufficient_funds():
```

## `pytest.approx` が必要な理由

浮動小数点の比較には誤差があります:

```python
assert 0.1 + 0.2 == 0.3   # False! 0.30000000000000004 != 0.3
assert 0.1 + 0.2 == pytest.approx(0.3)   # True (相対誤差 1e-6 以内)
```

## `with pytest.raises()` のパターン

```python
# 基本形
with pytest.raises(ValueError):
    divide(10, 0)

# メッセージの確認(正規表現で部分一致)
with pytest.raises(ValueError, match="ゼロ除算"):
    divide(10, 0)

# 例外オブジェクトを取り出す
with pytest.raises(ValueError) as exc_info:
    divide(10, 0)
assert "ゼロ除算" in str(exc_info.value)
```

## AAA パターンの重要性

テストを Arrange / Act / Assert の 3 段階に分けると:

1. **読みやすい**: 何をセットアップし、何を実行し、何を確認するかが明確
2. **保守しやすい**: セットアップを変えても Assert 部分を変える必要がない
3. **1 テスト 1 アサーション**: 複数の振る舞いを 1 つのテストに詰め込まない

フィクスチャ(`@pytest.fixture`)は Arrange の共通部分を切り出します。
