# レッスン 01: Python 環境構築と REPL

## 学習目標

- Python 3 のインストール状態を確認できる
- 仮想環境(virtual environment / venv)の目的と作り方を理解する
- pip でパッケージを管理できる
- REPL(Read-Eval-Print Loop)を使って素早く動作確認できる
- `.py` ファイルをスクリプトとして実行できる

---

## 1. Python のバージョン確認

ターミナルを開いて次を実行してください。

```bash
python3 --version
```

```
Python 3.12.3
```

バージョンが `3.10` 以上であれば問題ありません。
`3.12` 以上を推奨します。

> **なぜ python ではなく python3 か**
> macOS・Linux では `python` コマンドが Python 2 を指す場合があります。
> Python 2 は 2020 年にサポートが終了しており、現代の開発では使いません。
> 必ず `python3` と明示してください。

---

## 2. 仮想環境(venv)

### 2.1 なぜ仮想環境が必要か

Python には「グローバル環境」と「仮想環境」の 2 種類があります。

グローバル環境にパッケージをインストールし続けると、次の問題が起きます。

- プロジェクト A は `requests==2.28` を必要とし、プロジェクト B は `requests==2.31` を必要とする場合、両立できない
- チームメンバーの PC と自分の PC でバージョンが異なりバグが再現しない

仮想環境はプロジェクトごとに**独立した Python 実行環境**を作る仕組みです。

```
グローバル環境
  └── Python 3.12
       └── pip (パッケージ管理ツール)

プロジェクト A の仮想環境 (.venv)
  └── Python 3.12 のコピー
       ├── requests==2.28
       └── numpy==1.24

プロジェクト B の仮想環境 (.venv)
  └── Python 3.12 のコピー
       └── requests==2.31
```

### 2.2 仮想環境の作成と有効化

```bash
# プロジェクトディレクトリを作成
mkdir my_project
cd my_project

# 仮想環境を作成(.venv という名前のディレクトリが生成される)
python3 -m venv .venv

# 仮想環境を有効化(macOS / Linux)
source .venv/bin/activate

# 仮想環境を有効化(Windows PowerShell)
# .venv\Scripts\Activate.ps1
```

有効化するとプロンプトが変わります。

```
(.venv) $
```

この `(.venv)` が付いている間、`python` コマンドは仮想環境の Python を指します。

```bash
# 有効化後は python でも python3 と同じ
python --version
```

```
Python 3.12.3
```

### 2.3 仮想環境の無効化

```bash
deactivate
```

プロンプトから `(.venv)` が消えます。

### 2.4 .gitignore に追加する

仮想環境は Git で管理しません(容量が大きく、OS 依存のバイナリが含まれる)。

```bash
echo ".venv/" >> .gitignore
```

---

## 3. pip によるパッケージ管理

### 3.1 基本コマンド

```bash
# パッケージのインストール
pip install requests

# バージョン指定してインストール
pip install requests==2.31.0

# パッケージのアンインストール
pip uninstall requests

# インストール済みパッケージの一覧
pip list

# 依存関係をファイルに書き出す
pip freeze > requirements.txt

# requirements.txt からインストール
pip install -r requirements.txt
```

### 3.2 requirements.txt の使い方

```bash
pip freeze > requirements.txt
```

```
# requirements.txt の内容例
certifi==2024.2.2
charset-normalizer==3.3.2
idna==3.6
requests==2.31.0
urllib3==2.2.1
```

チームメンバーは次のコマンドで同じ環境を再現できます。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 4. REPL(対話型シェル)

REPL とは **R**ead-**E**val-**P**rint **L**oop の略で、コードを 1 行ずつ入力し、
即座に結果を確認できる対話型環境です。

```bash
python3
```

```
Python 3.12.3 (main, Apr  9 2024, 08:09:14)
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

`>>>` がプロンプトです。ここにコードを入力して Enter を押すと実行されます。

```python
>>> 1 + 2
3
>>> "hello" + " " + "world"
'hello world'
>>> 10 / 3
3.3333333333333335
>>> 10 // 3
3
>>> 10 % 3
1
```

REPL を終了するには `exit()` または `Ctrl + D` を押します。

> **REPL の活用法**
> - 新しい関数の挙動を確認する
> - データ構造を素早く試す
> - エラーメッセージの意味を調べる
>
> プロが使う高機能な REPL として **IPython** や **Jupyter Notebook** がありますが、
> まずは標準の REPL に慣れましょう。

---

## 5. スクリプトの実行

`.py` ファイルに書いたコードをファイルとして実行できます。

```bash
# hello.py を作成
cat > hello.py << 'EOF'
print("Hello, World!")
print("Python プログラミングを始めましょう")
EOF

# 実行
python3 hello.py
```

```
Hello, World!
Python プログラミングを始めましょう
```

### 5.1 スクリプトとしての実行可能化(macOS / Linux)

ファイルの先頭に **shebang(シバン)**を書くと、`python3` を省略して実行できます。

```python
#!/usr/bin/env python3
print("Hello, World!")
```

```bash
chmod +x hello.py
./hello.py
```

---

## 6. エディタで Python を書く

エディタで補完やエラー表示を効かせるには、**どのエディタでも同じ 2 つ**が必要です。

1. **その言語の拡張(言語サーバ)を入れる** — エディタがコードの構造を理解できるようになる
2. **使うインタプリタを、いま作った仮想環境のものに指定する**

手順 2 を忘れる人が非常に多く、**このレッスンで最も多い詰まりどころ**です。仮想環境に入れたはずのパッケージが「見つからない」と表示されたら、まずここを疑ってください。ターミナルでは動くのにエディタだけが赤線を引く、という症状になります。

VS Code の場合は、コマンドパレットから `Python: Select Interpreter` を選び、`./venv/bin/python` を指定します。他のエディタでも、同じ設定が別の名前で必ずあります。

これで補完・エラーのリアルタイム表示・デバッガが使えます。エディタの機能そのものは [Phase 3 レッスン 08: エディタを使いこなす](../../phase3-dev-tools/lessons/08-editor-mastery.md) で詳しく扱います。

---

## 💡 コラム: Python の名前はヘビではない

Python という名前は、ヘビではなくイギリスのコメディ番組「空飛ぶモンティ・パイソン」から取られました。作者のグイド・ヴァンロッサムが大ファンだったのです(公式ドキュメントに例として spam や eggs が頻出するのも、この番組のコントが元ネタです)。

開発が始まったのは1989年のクリスマス休暇。グイドは「オフィスが閉まっていて暇だったから、趣味のプロジェクトとして言語を書き始めた」と語っています。休暇の暇つぶしが、35年後に AI 開発と世界中の教育を支える言語になりました。

Python の設計哲学は一貫して「読みやすさ」です。これから文法を学ぶとき、「なぜこう書くのか」に迷ったら思い出してください — この言語は**書く人ではなく、読む人のために**設計されています。

---

## まとめ

| 概念           | コマンド / 操作                            |
|----------------|-------------------------------------------|
| バージョン確認  | `python3 --version`                       |
| 仮想環境作成    | `python3 -m venv .venv`                   |
| 仮想環境有効化  | `source .venv/bin/activate`               |
| 仮想環境無効化  | `deactivate`                              |
| パッケージ追加  | `pip install <name>`                      |
| 依存出力        | `pip freeze > requirements.txt`           |
| REPL 起動       | `python3`                                 |
| スクリプト実行  | `python3 script.py`                       |

---

## 確認問題

1. 仮想環境を使う理由を、具体的なシナリオを挙げて説明してください。
2. `pip freeze` と `pip list` の違いは何ですか?
3. `.venv/` を `.gitignore` に追加する理由を説明してください。
4. REPL で `2 ** 10` を実行すると何が表示されますか? (`**` は何を意味しますか?)
5. 仮想環境を有効化した状態で `which python` を実行すると何が表示されますか?

---

## よくある間違い

### 間違い 1: 仮想環境を有効化し忘れてインストールする

```bash
# 悪い例: 仮想環境を有効化せずに pip install
pip install requests

# 良い例
source .venv/bin/activate
pip install requests
```

有効化せずにインストールするとグローバル環境が汚染されます。
`pip list` を実行したとき、意図しないパッケージが大量に表示される場合は
グローバル環境にインストールしてしまっています。

### 間違い 2: .venv ディレクトリを Git にコミットする

仮想環境はサイズが大きく(数十〜数百 MB)、OS に依存するバイナリが含まれます。
必ず `.gitignore` に追加してください。

### 間違い 3: requirements.txt なしでコードを共有する

依存パッケージの情報がなければ、他の人があなたのコードを実行できません。
プロジェクトを共有する前に必ず `pip freeze > requirements.txt` を実行してください。

---

## 演習

`exercises/ex01_environment/` を参照してください。
