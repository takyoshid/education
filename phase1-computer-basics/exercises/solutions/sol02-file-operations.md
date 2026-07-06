# 解答 02: ファイル操作とパーミッション

---

## 問題 1: ディレクトリとファイルの作成

### 解答

```bash
# 方法1: mkdir -p でまとめて作成
$ mkdir -p ~/practice/phase1-ex02/project/src
$ mkdir -p ~/practice/phase1-ex02/project/docs
$ mkdir -p ~/practice/phase1-ex02/backup

# ファイルを作成
$ touch ~/practice/phase1-ex02/project/src/main.sh
$ touch ~/practice/phase1-ex02/project/src/utils.sh
$ touch ~/practice/phase1-ex02/project/docs/README.md
$ touch ~/practice/phase1-ex02/project/config.txt
```

### 確認

```bash
$ ls -R ~/practice/phase1-ex02/
```

### 思考プロセス

`mkdir -p` の `-p` オプションは「親ディレクトリが存在しない場合も含めて作成する」という意味です。
`mkdir project/src` だけでは `project` が存在しない場合にエラーになりますが、
`mkdir -p project/src` では `project` も自動的に作成されます。

---

## 問題 2: ファイルへの書き込みと表示

### 解答

```bash
# 方法1: echo を複数回使う（行ごと）
$ echo "APP_NAME=MyApp" > ~/practice/phase1-ex02/project/config.txt
$ echo "VERSION=1.0.0" >> ~/practice/phase1-ex02/project/config.txt
$ echo "AUTHOR=YourName" >> ~/practice/phase1-ex02/project/config.txt

# 方法2: ヒアドキュメント（複数行を一度に書ける）
$ cat > ~/practice/phase1-ex02/project/config.txt << 'EOF'
APP_NAME=MyApp
VERSION=1.0.0
AUTHOR=YourName
EOF
```

```bash
$ cat > ~/practice/phase1-ex02/project/docs/README.md << 'EOF'
# MyApp

これはサンプルアプリです。

## インストール方法

1. リポジトリをクローン
2. config.txt を編集
3. main.sh を実行
EOF
```

### 思考プロセス

**`>`（上書き）と `>>`（追記）の使い分け:**
- ファイルを新規作成・全体を書き直すとき: `>`
- 既存の内容に追加するとき: `>>`

**ヒアドキュメント（heredoc）** の構文:
```bash
cat > ファイル名 << 'EOF'
複数行の内容
...
EOF
```
`EOF` は任意の文字列（終了マーカー）。`'EOF'` のようにシングルクォートで囲むと、
ヒアドキュメント内の `$変数` が展開されなくなります（そのまま書き込まれる）。

---

## 問題 3: ファイルのコピーと移動

### 解答

```bash
$ cd ~/practice/phase1-ex02

# 1. config.txt を backup/ にコピー
$ cp project/config.txt backup/config_backup.txt

# 2. utils.sh を helpers.sh にリネーム（同じディレクトリ内の mv = リネーム）
$ mv project/src/utils.sh project/src/helpers.sh

# 3. README.md を backup/ にコピー
$ cp project/docs/README.md backup/
```

### 思考プロセス

**`cp` と `mv` の使い分け:**
- `cp`: 元ファイルを残してコピーを作る
- `mv`: 元ファイルを移動（または名前を変える）する。元ファイルは消える

**`cp` でのリネーム:**
```bash
cp old.txt new.txt   # old.txt を new.txt という名前でコピー（old.txt は残る）
```

**`mv` でのリネーム:**
```bash
mv old.txt new.txt   # old.txt を new.txt に名前変更（old.txt は消える）
```

---

## 問題 4: ファイル内容の追記と確認

### 解答

```bash
$ cd ~/practice/phase1-ex02

# 1. 追記（>> を使う！> では上書きになるので注意）
$ echo "DEBUG=false" >> project/config.txt
$ echo "LOG_LEVEL=info" >> project/config.txt

# 2. 内容と行数の確認
$ cat project/config.txt
APP_NAME=MyApp
VERSION=1.0.0
AUTHOR=YourName
DEBUG=false
LOG_LEVEL=info

$ wc -l project/config.txt
5 project/config.txt

# 3. 先頭3行と末尾2行
$ head -3 project/config.txt
APP_NAME=MyApp
VERSION=1.0.0
AUTHOR=YourName

$ tail -2 project/config.txt
DEBUG=false
LOG_LEVEL=info
```

### よくある間違い

`>>` と書くべきところを `>` と書いてしまうと、ファイルの内容が上書きされて消えてしまいます。
追記するか上書きするかを常に意識してください。

---

## 問題 5: パーミッションの操作

### 解答

```bash
$ cd ~/practice/phase1-ex02

# 1. 現在のパーミッション確認
$ ls -l project/src/main.sh
-rw-r--r--  1 takuya  staff  0 Jul  5 10:00 project/src/main.sh

# 2. 実行権限の付与
$ chmod 755 project/src/main.sh
$ chmod +x project/src/helpers.sh

# 3. 確認
$ ls -l project/src/
-rwxr-xr-x  1 takuya  staff  0 Jul  5 10:00 main.sh
-rwxr-xr-x  1 takuya  staff  0 Jul  5 10:00 helpers.sh

# 4. 権限設定
# backup/config_backup.txt: 所有者のみ読み書き可
$ chmod 600 backup/config_backup.txt
$ ls -l backup/config_backup.txt
-rw-------  1 takuya  staff  ... config_backup.txt

# project/docs/README.md: 全員が読める、所有者のみ書ける
$ chmod 644 project/docs/README.md
$ ls -l project/docs/README.md
-rw-r--r--  1 takuya  staff  ... README.md
```

### 思考プロセス

パーミッションの数値計算:
```
所有者のみ読み書き可（その他は一切不可）:
  owner: rw- = 4+2+0 = 6
  group: --- = 0
  others: --- = 0
  → 600

全員が読める、所有者のみ書ける:
  owner: rw- = 4+2+0 = 6
  group: r-- = 4
  others: r-- = 4
  → 644
```

**よく使うパーミッション値を覚えよう:**
- `644`: 通常のファイル（設定ファイルなど）
- `755`: 実行可能ファイル・ディレクトリ
- `600`: 秘密鍵などの機密ファイル
- `777`: 全員が全権限（セキュリティリスクがあるため通常は避ける）

---

## 問題 6: パーミッションを数値で読む

### 解答

```
-rwxr-xr-x  script.sh
  rwx = 4+2+1 = 7
  r-x = 4+0+1 = 5
  r-x = 4+0+1 = 5
  → 755

-rw-r--r--  config.txt
  rw- = 4+2+0 = 6
  r-- = 4+0+0 = 4
  r-- = 4+0+0 = 4
  → 644

-rw-------  secret.key
  rw- = 4+2+0 = 6
  --- = 0
  --- = 0
  → 600

drwxr-xr-x  public/
  rwx = 4+2+1 = 7
  r-x = 4+0+1 = 5
  r-x = 4+0+1 = 5
  → 755（d はディレクトリを表すが数値には含めない）
```

---

## 問題 7: パスの理解

カレントディレクトリ: `~/practice/phase1-ex02/project/src/`

### 解答

**1. `~/practice/phase1-ex02/project/config.txt`**
```
現在: ~/practice/phase1-ex02/project/src/
対象: ~/practice/phase1-ex02/project/config.txt

src/ から 1つ上（project/）に移動して config.txt
相対パス: ../config.txt
```

**2. `~/practice/phase1-ex02/backup/config_backup.txt`**
```
現在: ~/practice/phase1-ex02/project/src/
対象: ~/practice/phase1-ex02/backup/config_backup.txt

src/ から 2つ上（phase1-ex02/）に移動して backup/config_backup.txt
相対パス: ../../backup/config_backup.txt
```

**3. `~/practice/phase1-ex02/project/docs/README.md`**
```
現在: ~/practice/phase1-ex02/project/src/
対象: ~/practice/phase1-ex02/project/docs/README.md

src/ と docs/ は同じ階層（どちらも project/ 直下）
相対パス: ../docs/README.md
```

### 思考プロセス

相対パスを求めるコツ:
1. 現在地と目的地の共通の祖先ディレクトリを見つける
2. 現在地から共通祖先まで `../` を繰り返す
3. 共通祖先から目的地へのパスを繋げる

---

## 問題 8: 探索（grep + find）

### 解答

```bash
# 1. .sh ファイルをすべて表示
$ find ~/practice/phase1-ex02 -name "*.sh"
/Users/takuya/practice/phase1-ex02/project/src/main.sh
/Users/takuya/practice/phase1-ex02/project/src/helpers.sh

# 2. LOG_LEVEL を含む行を表示
$ grep "LOG_LEVEL" ~/practice/phase1-ex02/project/config.txt
LOG_LEVEL=info

# 3. DEBUG を含まない行を表示
$ grep -v "DEBUG" ~/practice/phase1-ex02/project/config.txt
APP_NAME=MyApp
VERSION=1.0.0
AUTHOR=YourName
LOG_LEVEL=info
```
