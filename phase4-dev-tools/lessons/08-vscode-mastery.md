# レッスン 08: VS Code 習熟

## このレッスンで学ぶこと

- VS Code の基本 UI とパネル構成
- 頻出キーボードショートカット
- マルチカーソルで複数行を同時編集する
- リファクタリング機能(名前変更・コード抽出)
- 組み込みデバッガの使い方
- Git 連携機能

---

## 1. VS Code の基本 UI

```
+----------------------------------+----------------------------------+
|  アクティビティバー              |  エディタ                        |
|  (左端のアイコン列)              |                                  |
|                                  |  ファイルの内容を編集する場所   |
|  [ファイル]  [検索]              |                                  |
|  [Git]      [デバッグ]           |  タブを複数開いて並べられる      |
|  [拡張機能]                      |                                  |
+----------------------------------+----------------------------------+
|  サイドバー                      |  パネル (ターミナル / 問題 / etc)|
|  (ファイルツリー、検索結果 etc)  |                                  |
|                                  |  $ git status                    |
|  src/                            |  On branch main                  |
|  ├── app.py                      |                                  |
|  └── utils.py                    |                                  |
+----------------------------------+----------------------------------+
|  ステータスバー(最下部)                                             |
|  ブランチ名 / エラー数 / 文字コード / 言語モード                    |
+----------------------------------------------------------------------+
```

---

## 2. 頻出キーボードショートカット

### ファイル操作

| 操作                          | Mac                    | Windows / Linux         |
|-------------------------------|------------------------|-------------------------|
| コマンドパレット               | Cmd + Shift + P        | Ctrl + Shift + P        |
| ファイルを素早く開く           | Cmd + P                | Ctrl + P                |
| 新しいファイル                 | Cmd + N                | Ctrl + N                |
| 保存                           | Cmd + S                | Ctrl + S                |
| すべて保存                     | Cmd + Option + S       | Ctrl + K, S             |
| ファイルを閉じる               | Cmd + W                | Ctrl + W                |
| サイドバーの表示/非表示        | Cmd + B                | Ctrl + B                |
| ターミナルを開く/閉じる        | Ctrl + `               | Ctrl + `                |

### 編集

| 操作                          | Mac                    | Windows / Linux         |
|-------------------------------|------------------------|-------------------------|
| 元に戻す                       | Cmd + Z                | Ctrl + Z                |
| やり直し                       | Cmd + Shift + Z        | Ctrl + Y                |
| 切り取り                       | Cmd + X                | Ctrl + X                |
| コピー                         | Cmd + C                | Ctrl + C                |
| 貼り付け                       | Cmd + V                | Ctrl + V                |
| 行を上/下に移動                 | Option + 上下キー      | Alt + 上下キー           |
| 行を上/下にコピー               | Option + Shift + 上下  | Alt + Shift + 上下       |
| 行を削除                       | Cmd + Shift + K        | Ctrl + Shift + K        |
| 行をコメントアウト              | Cmd + /                | Ctrl + /                |
| インデントを増やす/減らす       | Tab / Shift + Tab      | Tab / Shift + Tab        |
| すべて選択                     | Cmd + A                | Ctrl + A                |
| 選択範囲を拡張                  | Shift + Option + 右    | Shift + Alt + 右         |

### 検索・置換

| 操作                          | Mac                    | Windows / Linux         |
|-------------------------------|------------------------|-------------------------|
| ファイル内検索                 | Cmd + F                | Ctrl + F                |
| ファイル内置換                 | Cmd + H                | Ctrl + H                |
| プロジェクト全体を検索         | Cmd + Shift + F        | Ctrl + Shift + F        |
| プロジェクト全体で置換         | Cmd + Shift + H        | Ctrl + Shift + H        |
| 次の検索結果へ                 | Enter / F3             | Enter / F3              |

### 移動

| 操作                           | Mac                    | Windows / Linux         |
|--------------------------------|------------------------|-------------------------|
| 定義へジャンプ                  | F12                    | F12                     |
| 定義をのぞき見                  | Option + F12           | Alt + F12               |
| 参照一覧を表示                  | Shift + F12            | Shift + F12             |
| 行番号に移動                    | Ctrl + G               | Ctrl + G                |
| 前/次のエラーに移動              | F8 / Shift + F8        | F8 / Shift + F8         |
| ファイルの先頭/末尾             | Cmd + Home / End       | Ctrl + Home / End       |

---

## 3. マルチカーソル: 複数行を同時編集する

マルチカーソルは VS Code の最も強力な機能の一つです。同じ変更を複数の行に一度に適用できます。

### マルチカーソルの追加方法

**方法1: クリックで追加**

- `Option(Alt) + クリック` で任意の位置にカーソルを追加

**方法2: 同じ単語を選択**

```
Cmd(Ctrl) + D  -- カーソル位置の単語を選択し、次の同じ単語も選択する
Cmd(Ctrl) + Shift + L  -- ファイル内のすべての同じ単語を選択
```

**方法3: 矩形選択(列選択)**

```
Option(Alt) + Shift + ドラッグ  -- 矩形範囲を選択
Option(Alt) + Shift + 上下キー  -- カーソルを上下に増やす
```

### マルチカーソルの実践例

**例1: 複数の変数名を一度に変更する**

```python
# 変更前
user_name = "Alice"
print(user_name)
return user_name

# user_name をすべて選択して username に変える
# 1. "user_name" の上にカーソルを置く
# 2. Cmd+D を 3 回押して 3 つの user_name を選択
# 3. "username" と入力

# 変更後
username = "Alice"
print(username)
return username
```

**例2: 各行の末尾にセミコロンを追加する**

```python
# 変更前
x = 1
y = 2
z = 3

# 1. Option(Alt) + クリックで各行の末尾にカーソルを置く
# 2. ";" と入力

# ターミナルコマンドの一覧を SQL に変換するときなど大量変換に便利
```

**例3: 列を一度に編集する**

```
# 変更前(縦に並んだ数値を変えたい)
item_1 = 10
item_2 = 20
item_3 = 30

# 1. "10" の前をクリック
# 2. Option + Shift + 下キーで 3 行にカーソルを拡張
# 3. Cmd + Shift + Right でそれぞれの数値を選択
# 4. 新しい値を入力
```

---

## 4. リファクタリング機能

### シンボルの名前変更 (Rename Symbol)

変数・関数・クラスの名前を、参照しているすべての場所で一度に変更します。

```
F2  -- 名前変更ダイアログを開く
```

これは単純な「文字列置換」ではなく、同じスコープの参照だけを正しく変更します。

```python
# 変更前
def calculate_total(items):
    result = 0
    for item in items:
        result += item.price
    return result

total = calculate_total(cart_items)
print(f"Total: {total}")

# calculate_total の上で F2 を押して "compute_total" に変更
# --> calculate_total を参照しているすべての箇所が変更される
```

### コードアクション (Quick Fix)

エラーや警告の行で電球アイコンをクリック(または `Cmd + .` / `Ctrl + .`)すると、自動修正の候補が表示されます。

よく使うクイックフィックス:
- 未使用の import を削除
- 欠けている import を追加
- メソッドのシグネチャを修正

### ピーク定義 (Peek Definition)

```
Option + F12 (Alt + F12)
```

定義元のコードを、現在のファイルを離れずに確認できます。

---

## 5. 組み込みデバッガ

デバッガを使うと、プログラムを一行ずつ実行しながら変数の値を確認できます。`print()` デバッグより効率的です。

### ブレークポイントの設定

エディタの行番号の左側をクリックすると、赤い丸のブレークポイントが設定されます。プログラムはその行で一時停止します。

### デバッガの起動

1. `launch.json` を作成する(初回のみ)
   - サイドバーのデバッグアイコン(虫のマーク)をクリック
   - 「launch.json ファイルを作成します」をクリック
   - Python を選択

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

2. `F5` でデバッグ開始

### デバッガの操作

| 操作               | ショートカット | 説明                                   |
|--------------------|----------------|----------------------------------------|
| Continue           | F5             | 次のブレークポイントまで実行            |
| Step Over          | F10            | 現在の行を実行して次の行へ(関数に入らない) |
| Step Into          | F11            | 現在の行を実行して関数の中に入る        |
| Step Out           | Shift + F11    | 現在の関数を最後まで実行して抜け出る    |
| Stop               | Shift + F5     | デバッグを終了                          |

### デバッガのパネル

ブレークポイントで停止すると、左側のデバッグパネルに以下が表示されます:

- **Variables**: 現在のスコープの変数と値
- **Watch**: 特定の式を監視して値を確認
- **Call Stack**: 関数の呼び出し履歴
- **Breakpoints**: 設定中のブレークポイント一覧

### デバッグコンソール

デバッグ中に任意の式を評価できます。

```python
# デバッグコンソールに入力
len(items)
items[0].price
sum(item.price for item in items)
```

### 実践: バグを見つける

```python
# buggy_calculator.py
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)

data = [10, 20, 30, 40, 50]
result = calculate_average(data)
print(f"Average: {result}")

# さらに別のバグ: 空リストを渡したら ZeroDivisionError が起きる
# ブレークポイントを設定して各ステップの total の値を確認する
```

---

## 6. VS Code の Git 連携

VS Code は Git との連携機能が組み込まれています。

### ソース管理パネル

- サイドバーのソース管理アイコン(フォークのマーク)をクリック
- 変更されたファイルの一覧が表示される
- ファイル名をクリックすると diff が表示される
- `+` ボタンで `git add`、コミットメッセージを入力してチェックマークで `git commit`

### インラインの diff 表示

変更した行の左端に色付きのバーが表示されます:
- 緑: 追加した行
- 青: 変更した行
- 赤の三角: 削除した行

行のバーをクリックするとその変更の diff と、変更を元に戻すボタンが表示されます。

### GitLens 拡張機能

GitLens は VS Code の Git 機能を大幅に強化する人気拡張機能です。

主な機能:
- 各行の横に「誰がいつ変更したか」(git blame)を表示
- コミット履歴をファイル・行・ブランチ単位で確認
- コミット間の diff を視覚的に比較

---

## 7. おすすめ拡張機能

| 拡張機能名              | 用途                                       |
|-------------------------|--------------------------------------------|
| Python (Microsoft)      | Python の補完・デバッグ・Linting           |
| GitLens                 | Git の高度な連携機能                       |
| Prettier                | コードの自動フォーマット                   |
| ESLint                  | JavaScript / TypeScript の静的解析         |
| Path Intellisense       | ファイルパスの補完                         |
| indent-rainbow          | インデントを色分けして見やすくする          |
| Error Lens              | エラーをインラインで表示                   |
| REST Client             | HTTP リクエストを VS Code から送れる       |

---

## まとめ

### 最優先で覚えるショートカット TOP 10

| 操作                  | Mac              | Windows / Linux    |
|-----------------------|------------------|--------------------|
| コマンドパレット       | Cmd + Shift + P  | Ctrl + Shift + P   |
| ファイルを素早く開く   | Cmd + P          | Ctrl + P           |
| 保存                   | Cmd + S          | Ctrl + S           |
| ターミナルを開く       | Ctrl + `         | Ctrl + `           |
| 行をコメントアウト     | Cmd + /          | Ctrl + /           |
| 定義へジャンプ         | F12              | F12                |
| 名前変更               | F2               | F2                 |
| 次の同じ単語を選択     | Cmd + D          | Ctrl + D           |
| 行を上下に移動         | Option + 上下    | Alt + 上下          |
| デバッグ開始           | F5               | F5                 |

---

## 確認問題

1. `Cmd + D`(Ctrl + D)を 3 回押したとき、何が起きますか?

2. マルチカーソルを使って、次のコードの `old_name` を `new_name` に変更する手順を説明してください。
   ```python
   old_name = "Alice"
   print(old_name)
   return old_name
   ```

3. F2 による「シンボルの名前変更」と `Cmd + H` による「ファイル内置換」の違いは何ですか? どちらが安全ですか?

4. デバッガの Step Over(F10)と Step Into(F11)の違いを説明してください。

5. ブレークポイントで停止したとき、現在の変数の値を確認するには、デバッグパネルのどの部分を見ればよいですか?

---

前のレッスン: [レッスン 07: 実務ツール](./07-practical-tools.md)

演習: [演習へ進む](../exercises/ex01-first-commit.md)
