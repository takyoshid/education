# 演習 09 解説: オブジェクト指向

## 問題 4: `@property` の仕組み

`@property` はデコレータで、メソッドを「属性のように」アクセスできるようにします。

```python
class Temperature:
    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("...")
        self._celsius = value
```

`t.celsius` と書くと getter が呼ばれ、`t.celsius = 100` と書くと setter が呼ばれます。
外部からは普通の属性アクセスに見えますが、内部でバリデーションを実行できます。

`@celsius.setter` の `celsius` は **getter の名前と一致** させる必要があります。

## 問題 7: イテレータプロトコル

Python の `for` ループは内部で次の流れで動作します:

1. `iter(iterable)` を呼ぶ → `__iter__` が呼ばれ、イテレータを返す
2. `next(iterator)` を繰り返し呼ぶ → `__next__` が呼ばれ、次の値を返す
3. `StopIteration` が上がるとループが終了する

`NumberRange` は `__iter__` が `self` を返すため、イテレータかつイテラブルです。
これにより `for` ループと直接使えます。

重要な注意点:
- `__iter__` で `self._current = self.start` にリセットしないと、
  同じオブジェクトを 2 回 `for` でループしたとき 2 回目が空になります。

## 問題 8: コンテキストマネージャ

`with` 文は次の流れで動作します:

```python
with Timer("label") as t:
    処理

# 上記は以下と等価
t = Timer("label")
t.__enter__()
try:
    処理
except:
    if not t.__exit__(*sys.exc_info()):
        raise
else:
    t.__exit__(None, None, None)
```

`__exit__` の引数:
- `exc_type`: 例外クラス(例外がなければ `None`)
- `exc_val`: 例外インスタンス
- `exc_tb`: トレースバックオブジェクト

`return False`(または `return None`) → 例外を再送出
`return True` → 例外を抑制

ファイルを安全に閉じる `with open(...)` も同じ仕組みです。
