# 演習 01 解説: 環境構築

この演習は「実行環境そのもの」が対象なので、実行可能な `.py` ではなくコマンドと解説で示します。表示されるバージョン番号やパスは環境によって異なります。**出力が一字一句同じである必要はありません。**

---

## 基本

### 問題 1: Python のバージョン確認

```bash
python3 --version
# Python 3.13.0
```

**`python` ではなく `python3` を使う**理由: macOS や一部の Linux では `python` が存在しないか、古い Python 2 を指すことがあります。迷ったら `python3` です。

複数の Python が入っている場合、どれが使われているかを確認します。

```bash
which -a python3
# /opt/homebrew/bin/python3
# /usr/bin/python3          ← OS 付属のもの。触らない
```

> **重要**: OS 付属の Python(`/usr/bin/python3`)にパッケージを入れないでください。OS の一部が壊れることがあります。だから仮想環境を使います。

### 問題 2〜3: 仮想環境の作成と有効化

```bash
mkdir my_first_project
cd my_first_project

python3 -m venv .venv        # .venv という名前が事実上の標準
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate     # Windows (PowerShell)
```

有効化されるとプロンプトの先頭に `(.venv)` が付きます。

```bash
(.venv) $ which python
/path/to/my_first_project/.venv/bin/python    ← 仮想環境の中を指している

(.venv) $ pip list
Package    Version
---------- -------
pip        24.x
```

初期状態は `pip` だけ、あるいはほぼ空です。これが仮想環境の要点で、**プロジェクトごとに独立した空っぽの箱**を作っています。

抜けるときは `deactivate` です。

### なぜ仮想環境が必要か

仮想環境を使わないと、全プロジェクトが同じ場所にライブラリを入れます。

```
プロジェクトA: requests 2.25 が必要
プロジェクトB: requests 2.32 が必要
→ 片方しか入れられない(依存関係の地獄)
```

仮想環境は、この問題を「プロジェクトごとに箱を分ける」ことで解決します。Node.js の `node_modules`、Ruby の bundler と同じ発想です。

### 問題 4: 依存関係の記録

```bash
pip install requests
pip freeze > requirements.txt
cat requirements.txt
```

```
certifi==2024.x.x
charset-normalizer==3.x.x
idna==3.x
requests==2.32.x
urllib3==2.x.x
```

**`requests` しか入れていないのに5行ある**のはなぜか。`requests` が依存するライブラリ(推移的依存)も一緒に入るからです。

`pip freeze` は「今この環境に入っている全部」を出力します。これには利点と欠点があります。

| | 利点 | 欠点 |
|---|---|---|
| `pip freeze` の全列挙 | 環境を完全に再現できる | 「自分が直接使うもの」が分からなくなる |

実務では、直接使うものだけを手で書いた `requirements.txt` と、`pip freeze` で固めた `requirements.lock` を分けることがあります。Phase 6 以降の教材では前者の形を使っています。

> **今回のレビューで見つかった実例**: この教材の Phase 6 は、直接 import しているのに `requirements.txt` に書かれていないパッケージがあり、クリーンな環境で動きませんでした。「たまたま他のパッケージ経由で入っていた」ために、作者の環境では動いていたのです。**直接使うものは必ず明示する**。

### 問題 5: `hello.py`

```python
import sys

print(f"Python {sys.version}")
print("Hello, World!")
```

```bash
python3 hello.py
```

```
Python 3.13.0 (main, Oct  7 2024, 05:02:14) [Clang 16.0.0 ]
Hello, World!
```

`sys.version` は人間向けの文字列です。プログラムでバージョンを判定するなら `sys.version_info` を使います。

```python
if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10 以上が必要です")
```

文字列比較(`sys.version > "3.9"`)は `"3.10" < "3.9"` になるので**必ず間違えます**。タプル比較を使ってください。

---

## 応用

### 問題 6: REPL での確認

```bash
python3
```

```python
>>> 2 ** 32
4294967296
>>> 10 / 3
3.3333333333333335        # / は常に float を返す
>>> 10 // 3
3                         # // は切り捨て除算
>>> 10 % 3
1                         # 余り
>>> "Python" * 3
'PythonPythonPython'      # 文字列 × 整数 は繰り返し
```

注目すべき点:

- **`/` は整数同士でも float を返す**(Python 3 の仕様。Python 2 とは違う)
- `10 / 3` が `3.3333333333333335` と末尾が `5` になるのは、浮動小数点の丸め誤差です(レッスン 02)
- `2 ** 32` が桁あふれしないのは、Python の整数に上限が無いためです。C や Java とは違います

REPL を抜けるには `exit()` または `Ctrl+D` です。

### 問題 7: 仮想環境の破棄と再作成

```bash
deactivate
rm -rf .venv

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pip list        # 元に戻っていることを確認
```

**この操作に慣れておくことが重要です。**仮想環境は「壊れたら消して作り直せばいい」使い捨ての箱です。中で何かおかしくなったら、原因を追う前にまず作り直す、で解決することが多くあります。

そのために `.venv/` は **Git にコミットしません**(`.gitignore` に入れる)。コミットするのは `requirements.txt` だけです。「環境そのもの」ではなく「環境の作り方」を共有する、という考え方です。

```gitignore
.venv/
__pycache__/
*.pyc
```

---

## 挑戦

### 問題 8: shebang で実行可能にする

```python
#!/usr/bin/env python3
import sys

print(f"Python {sys.version}")
print("Hello, World!")
```

```bash
chmod +x hello.py       # 実行権限を付ける
./hello.py
```

**`#!/usr/bin/env python3` と書く理由**(`#!/usr/bin/python3` ではなく):

`env` は `PATH` から `python3` を探します。つまり**仮想環境を有効化していれば、その中の python3 が使われます**。パスを直接書くと、常にシステムの Python が使われ、仮想環境に入れたライブラリが見つかりません。

```bash
#!/usr/bin/python3        # ✗ 常に /usr/bin/python3
#!/usr/bin/env python3    # ○ PATH を尊重する
```

shebang は 1 行目でなければ効きません。Windows では無視されます。

### 問題 9: IPython

```bash
pip install ipython
ipython
```

標準の REPL との主な違い:

| 機能 | 内容 |
|---|---|
| `obj?` | オブジェクトのヘルプを表示 |
| `obj??` | ソースコードを表示 |
| `Tab` | 補完が効く |
| `%timeit expr` | 実行時間を計測 |
| `%who` | 定義済みの変数一覧 |
| `!ls` | シェルコマンドを実行 |
| 貼り付け | 複数行をそのまま貼れる |

```python
In [1]: %timeit sum(range(1000))
7.32 µs ± 45.3 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

In [2]: import requests
In [3]: requests.get?
```

Phase 3 のアルゴリズム学習では `%timeit` が計測に役立ちます。

---

## この演習で身につく判断

| 場面 | 判断 |
|---|---|
| Python を実行する | `python3`。システムの Python は汚さない |
| プロジェクトを始める | 最初に `python3 -m venv .venv` |
| 依存を記録する | 直接使うものは必ず明示する |
| 環境がおかしい | 原因を追う前に作り直してみる |
| Git にコミットする | `.venv/` ではなく `requirements.txt` |
| バージョンを判定する | `sys.version_info`(タプル比較) |
| shebang を書く | `#!/usr/bin/env python3` |

---

## よくあるつまずき

**`source .venv/bin/activate` が「そんなファイルはない」と言われる**
`python3 -m venv .venv` を実行したディレクトリにいますか。`ls -a` で `.venv` があるか確認してください。Windows なら `.venv\Scripts\activate` です。

**有効化したのに `pip install` したパッケージが見つからない**
別のターミナルタブで実行していませんか。仮想環境の有効化はシェルごとです。新しいタブを開いたら再度 `activate` が必要です。

**`pip` と `python` で見えている環境が違う**
`which python` と `which pip` を比べてください。両方が `.venv/bin/` を指しているのが正常です。ずれている場合は `python3 -m pip install ...` の形で実行すると、必ず対応する pip が使われます。
