# 演習 07 解説: ファイル入出力と例外処理

実行可能な解答は [`ex07_solutions.py`](ex07_solutions.py) にあります。ここでは「なぜそう書くか」を説明します。

この演習には、**Phase 7 以降で何度も出てくる考え方**が3つ埋まっています。エンコーディング、例外の粒度、そして「壊さない書き込み」です。

## 1. `encoding="utf-8"` を省略してはいけない

```python
path.write_text(text)                      # ✗ 環境依存
path.write_text(text, encoding="utf-8")    # ○
```

`open()` や `read_text()` で encoding を省略すると、**OS の既定エンコーディングが使われます**。macOS / Linux では UTF-8 ですが、Windows では長らく cp932(Shift_JIS 系)でした。

つまり、あなたの Mac で動いたコードが、チームメイトの Windows で日本語が文字化けする、あるいは `UnicodeDecodeError` で落ちます。**「私の環境では動く」の典型的な発生源**です。

Python 3.15 で既定が UTF-8 になる予定ですが、それまでは常に明示してください。省略していい理由はありません。

## 2. `except Exception` を書かない

```python
# ✗ 何が起きても握りつぶす
try:
    return path.read_text(encoding="utf-8")
except Exception:
    return None

# ○ 想定した失敗だけを捕まえる
try:
    return path.read_text(encoding="utf-8")
except FileNotFoundError:
    return None
except PermissionError:
    return None
```

広く捕まえると、**想定していない障害まで「ファイルが無かった」ことにされます**。ディスク障害、権限の設定ミス、エンコーディングエラー — どれも本来は気づくべき問題です。

例外処理の原則は「**回復できる失敗だけを捕まえる**」。回復方法が思いつかない例外は、捕まえずに落としたほうが安全です。落ちれば気づけますが、握りつぶすと誰も気づきません。

### `finally` は「必ず実行される」

```python
finally:
    print("処理終了")
```

`return` した後でも、例外が飛んでも、`finally` は必ず実行されます。ファイルを閉じる、ロックを外す、接続を返す — こうした後始末に使います。

ただし、ファイルについては `with` 文を使えば `finally` を書く必要はありません。`with` は「後始末を忘れられない構文」です。

## 3. 上書きは「一時ファイル → 置換」

問題 5 の `save_config()` で、なぜ直接書かないのか:

```python
# ✗ 危険
with path.open("w") as f:
    json.dump(config, f)
```

`open(path, "w")` を実行した瞬間に、**既存の中身は消えます**。この後で書き込み中にプロセスが落ちたり、ディスクが満杯になったりすると、設定ファイルは「空、または途中まで書かれた壊れた状態」で残ります。元のデータは戻りません。

```python
# ○ 安全
tmp = path.with_suffix(path.suffix + ".tmp")
with tmp.open("w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
tmp.replace(path)
```

`Path.replace()` は同一ファイルシステム上では**アトミック**です。つまり「古い内容」か「新しい内容」のどちらかしか観測されず、中途半端な状態が存在しません。

この「一時ファイルに書いてから置換する」パターンは **atomic write** と呼ばれ、Phase 2 の実技試験でも要求されます。設定ファイル、キャッシュ、レポート出力 — 上書きするものすべてで使ってください。

## 4. デフォルト値は `.copy()` して返す

```python
except FileNotFoundError:
    return DEFAULT_CONFIG.copy()   # .copy() を忘れない
```

`.copy()` を忘れると、呼び出し側が返り値を書き換えたときに `DEFAULT_CONFIG` 自体が変わります。次に読んだときには「デフォルト値」がもう別物です。

レッスン 10 の「ミュータブルなデフォルト引数」とまったく同じ罠が、モジュール変数の形で現れたものです。**共有されているミュータブルを返さない**。

## 5. 例外クラスは階層で設計する

```python
class CSVError(Exception): ...            # 基底
class CSVParseError(CSVError): ...        # 形式が不正
class CSVValidationError(CSVError): ...   # 値が不正
```

なぜ2つに分けるのか。**呼び出し側の対処が違うから**です。

| 例外 | 意味 | 呼び出し側の典型的な対処 |
|---|---|---|
| `CSVParseError` | ファイルの構造が壊れている | 処理全体を中断する |
| `CSVValidationError` | 構造は正しいが値が業務ルール違反 | その行だけ飛ばして続行する選択肢がある |

そして基底クラス `CSVError` があることで、「このパーサー由来のエラーだけまとめて捕まえる」ことができます。

```python
except CSVError as exc:     # 両方まとめて
except CSVValidationError:  # 値の問題だけ
```

**例外の分類は、呼び出し側が取りうる行動の分類**です。行動が同じなら分ける必要はありません。

### `raise ... from exc` を付ける

```python
raise CSVValidationError(f"{lineno}行目: ...") from exc
```

`from exc` を付けると、トレースバックに「元の原因」が残ります。付けないと `ValueError` が起きたという情報が消え、デバッグ時に困ります。

### エラーメッセージに行番号を入れる

```python
f"{lineno}行目: age が整数ではありません: {age_str!r}"
```

「エラーが発生しました」では利用者は直せません。**どこが、どう悪くて、何を期待していたか**の3点を書きます。`!r` を付けると `'thirty'` のように引用符付きで表示され、空白や不可視文字の混入にも気づけます。

## 6. 世代バックアップは「後ろから」ずらす

```python
for i in range(generations - 1, 0, -1):   # 2, 1 の順
    ...
```

前から `bak.1 -> bak.2` と動かすと、その時点で既存の `bak.2` を上書きしてしまいます。**古い方から押し出す**のが正解です。

```
先に bak.3 を削除
bak.2 -> bak.3
bak.1 -> bak.2
本体   -> bak.1
新しい内容を本体へ
```

配列を1つずらす操作全般に共通する考え方で、Phase 5 の配列操作でも同じ判断が出てきます。

---

## 検証してみよう

解答スクリプトは一時ディレクトリの中だけで動き、終了時に自分で片付けます。カレントディレクトリにゴミを残しません。

```bash
python3 ex07_solutions.py
```

余力があれば、次を自分で確かめてください。

1. `save_config()` の `tmp.replace(path)` の行をコメントアウトし、代わりに直接 `path.open("w")` で書く実装にして、書き込み途中で `raise` してみる。既存ファイルがどうなるか
2. `except FileNotFoundError` を `except Exception` に変えて、読み取り権限の無いファイルを渡してみる。何が起きたか分かるか
3. `encoding="utf-8"` を全部消して、`LANG=C python3 ex07_solutions.py` で実行してみる

## この演習で身につく判断

| 場面 | 判断 |
|---|---|
| ファイルを開く | `encoding` を必ず明示する |
| 例外を捕まえる | 回復できる失敗だけを、狭く捕まえる |
| ファイルを上書きする | 一時ファイルに書いてから `replace()` |
| デフォルト値を返す | ミュータブルなら `.copy()` |
| 例外クラスを作る | 呼び出し側の対処が違うものだけ分ける |
| エラーを報告する | どこが・どう悪く・何を期待したか |
