# 演習 01: 環境構築

## 基本

1. ターミナルで Python のバージョンを確認し、3.10 以上であることを確認せよ。
2. `my_first_project` というディレクトリを作成し、その中に仮想環境を作れ。
3. 仮想環境を有効化し、`pip list` で初期状態のパッケージ一覧を確認せよ。
4. `requests` ライブラリをインストールし、`pip freeze > requirements.txt` を実行せよ。
5. 次の内容の `hello.py` を作成し、実行せよ。

   ```python
   import sys
   print(f"Python {sys.version}")
   print("Hello, World!")
   ```

## 応用

6. REPL を起動し、次の計算を確認せよ。
   - `2 ** 32`
   - `10 / 3`
   - `10 // 3`
   - `10 % 3`
   - `"Python" * 3`

7. 仮想環境を削除し、再作成して `requirements.txt` からインストールし直せ。

## 挑戦

8. `hello.py` を shebang 付きで実行可能にし、`./hello.py` で実行できることを確認せよ(macOS/Linux)。
9. `pip install ipython` を実行し、IPython REPL の使い方を調べよ。
