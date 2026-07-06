# Lesson 07: パッケージマネージャと開発環境

## 学習目標

- パッケージマネージャ（package manager）の役割を理解する
- Homebrew（macOS）の基本的な使い方を習得する
- apt（Ubuntu/Debian Linux）の基本的な使い方を習得する
- 開発環境を整えるための典型的な手順を理解する

---

## 1. パッケージマネージャとは

パッケージマネージャは、ソフトウェア（パッケージ）の**インストール・アップデート・削除を管理するツール**です。

**パッケージマネージャがない場合:**
1. 公式サイトにアクセス
2. インストーラーをダウンロード
3. インストール実行
4. 依存するライブラリが必要な場合は繰り返す
5. アップデートの確認・適用を手動で行う

**パッケージマネージャがある場合:**
```bash
$ brew install git   # これだけ
```

**主なメリット:**
- 依存関係（dependency）を自動解決する
- コマンド一つでインストール・削除できる
- インストール済みパッケージを一覧管理できる
- 一括アップデートができる

---

## 2. Homebrew（macOS）

### Homebrew とは

Homebrew は macOS（および Linux）用のパッケージマネージャです。公式サイト: https://brew.sh

### インストール

```bash
# 公式サイトのインストールコマンド（2024年時点）
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

インストール後、指示に従って PATH の設定を行います（M1/M2 Mac では `/opt/homebrew/bin` を PATH に追加）。

```bash
# インストール確認
$ brew --version
Homebrew 4.x.x
```

### 基本コマンド

#### パッケージのインストール（install）

```bash
# git をインストール
$ brew install git

# 複数のパッケージを一度にインストール
$ brew install git node python

# インストール時の出力例
==> Downloading https://...
==> Installing git
==> Summary
  /opt/homebrew/Cellar/git/2.45.0: 1,680 files, 49.4MB
```

#### インストール済みパッケージの確認（list）

```bash
$ brew list
git
node
python@3.11
...
```

#### パッケージ情報の確認（info）

```bash
$ brew info git
==> git: stable 2.45.0 (bottled), HEAD
Distributed revision control system
https://git-scm.com
/opt/homebrew/Cellar/git/2.45.0 (1,680 files, 49.4MB) *
  Poured from bottle using the formulae.brew.sh API on 2024-07-05
...
```

#### パッケージの検索（search）

```bash
$ brew search python
==> Formulae
python@3.11  python@3.12  python@3.9  ...
```

#### アップデート

```bash
# Homebrew 自体をアップデート
$ brew update

# インストール済みパッケージをアップデート
$ brew upgrade

# 特定のパッケージのみアップデート
$ brew upgrade git
```

#### パッケージの削除（uninstall）

```bash
$ brew uninstall git
```

#### 問題の診断

```bash
# Homebrew の環境をチェック
$ brew doctor
```

### Cask（GUI アプリのインストール）

Homebrew Cask を使うと GUI アプリも管理できます。

```bash
# VS Code をインストール
$ brew install --cask visual-studio-code

# Google Chrome をインストール
$ brew install --cask google-chrome

# Cask でインストール済みのアプリ一覧
$ brew list --cask
```

### Brewfile（環境の再現）

`Brewfile` に必要なパッケージを記述しておくと、新しい Mac でも一発で環境を再現できます。

```bash
# 現在の環境を Brewfile に書き出す
$ brew bundle dump

# Brewfile の例
# ファイル名: Brewfile
brew "git"
brew "node"
brew "python@3.11"
cask "visual-studio-code"
cask "iterm2"

# Brewfile から一括インストール
$ brew bundle
```

---

## 3. apt（Ubuntu / Debian Linux）

### apt とは

`apt`（Advanced Package Tool）は Ubuntu、Debian などの Linux ディストリビューション（distribution）で使われるパッケージマネージャです。

Linux を使う場合（クラウドサーバーなど）は必須の知識です。

### 基本コマンド

#### パッケージリストの更新

```bash
# パッケージの情報を最新に更新（インストール前に必ず実行）
$ sudo apt update
```

#### パッケージのインストール

```bash
# git をインストール
$ sudo apt install git

# 複数のパッケージを一度にインストール
$ sudo apt install git curl wget vim

# 確認なしでインストール（-y オプション）
$ sudo apt install -y git
```

#### インストール済みパッケージの更新

```bash
# すべてのパッケージを最新版にアップデート
$ sudo apt upgrade

# update と upgrade を続けて実行（慣用句）
$ sudo apt update && sudo apt upgrade -y
```

#### パッケージの削除

```bash
# パッケージを削除（設定ファイルは残す）
$ sudo apt remove git

# パッケージと設定ファイルを完全に削除
$ sudo apt purge git

# 不要になった依存パッケージを削除
$ sudo apt autoremove
```

#### パッケージの検索

```bash
$ apt search python3
$ apt-cache search nginx
```

#### パッケージ情報の確認

```bash
$ apt show git
Package: git
Version: 1:2.43.0-1ubuntu7
...
```

### Homebrew vs apt の比較

| 項目 | Homebrew | apt |
|------|----------|-----|
| 対応 OS | macOS（Linux も可） | Ubuntu/Debian Linux |
| コマンド | `brew install` | `sudo apt install` |
| 管理者権限 | 不要（ユーザー権限） | 必要（sudo） |
| パッケージ数 | 多い（特に開発ツール） | 多い（特にシステム系） |

---

## 4. 典型的な開発環境の構築

### macOS での開発環境セットアップ例

```bash
# 1. Homebrew のインストール（前述）

# 2. 必須ツールのインストール
$ brew install git
$ brew install curl wget

# 3. プログラミング言語
$ brew install node          # Node.js (JavaScript)
$ brew install python@3.11   # Python
$ brew install go            # Go

# 4. エディタ・ツール
$ brew install --cask visual-studio-code
$ brew install --cask iterm2

# 5. Git の初期設定
$ git config --global user.name "Your Name"
$ git config --global user.email "your@email.com"
$ git config --global core.editor "vim"

# 6. シェルのカスタマイズ（zsh の場合）
# ~/.zshrc に追記
$ cat >> ~/.zshrc << 'EOF'
# エイリアスの設定
alias ll='ls -la'
alias ..='cd ..'
alias ...='cd ../..'

# プロンプトのカスタマイズ（例）
export PS1="%n@%m %1~ %# "
EOF

$ source ~/.zshrc
```

### Ubuntu サーバーでの開発環境セットアップ例

```bash
# 1. パッケージリストを更新
$ sudo apt update

# 2. 基本ツールをインストール
$ sudo apt install -y git curl wget vim build-essential

# 3. Node.js（nvm 経由が推奨）
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
$ source ~/.bashrc
$ nvm install --lts
$ node --version

# 4. Python
$ sudo apt install -y python3 python3-pip
$ python3 --version

# 5. Git の設定
$ git config --global user.name "Your Name"
$ git config --global user.email "your@email.com"
```

---

## 5. バージョン管理ツール（言語別）

プログラミング言語のバージョンを管理する専用ツールがあります。複数プロジェクトで異なるバージョンを使い分けるために重要です。

| 言語 | ツール名 | 説明 |
|------|----------|------|
| Node.js | `nvm`（Node Version Manager） | Node.js のバージョン切り替え |
| Python | `pyenv` | Python のバージョン切り替え |
| Ruby | `rbenv` / `rvm` | Ruby のバージョン切り替え |
| Java | `sdkman` | JDK のバージョン切り替え |

```bash
# pyenv でのバージョン管理例
$ brew install pyenv
$ pyenv install 3.11.9
$ pyenv global 3.11.9
$ python --version
Python 3.11.9
```

---

## 6. .dotfiles（設定ファイルの管理）

`~/.zshrc` や `~/.gitconfig` などの設定ファイルを**dotfiles（ドットファイル）**と呼びます。
これらを Git で管理すると、新しい PC でもすぐに同じ環境を再現できます。

```bash
# dotfiles リポジトリの作成例
$ mkdir ~/dotfiles
$ cd ~/dotfiles
$ cp ~/.zshrc .
$ cp ~/.gitconfig .
$ git init
$ git add .
$ git commit -m "Initial dotfiles"
# GitHub にプッシュ...
```

多くのエンジニアが自分の dotfiles を GitHub で公開しており、参考になります。

---

## まとめ

- パッケージマネージャはソフトウェアのインストール・管理を効率化する
- macOS では Homebrew（`brew install`）、Ubuntu では apt（`sudo apt install`）
- インストール前に必ず `brew update` / `sudo apt update` でパッケージリストを更新する
- GUI アプリは macOS では `brew install --cask` でインストールできる
- 開発言語のバージョン管理には nvm（Node.js）や pyenv（Python）などを使う

---

## 確認問題

**Q1.** パッケージマネージャを使うメリットを3つ挙げてください。

**Q2.** macOS で `wget` をインストールするコマンドを書いてください。インストール後、バージョンを確認するコマンドも書いてください。

**Q3.** Homebrew でインストール済みのパッケージを全部アップデートする一連のコマンドを書いてください。

**Q4.** Ubuntu サーバーで `nginx`（Web サーバーソフトウェア）をインストールするコマンドを書いてください。

**Q5.** `brew install git` と `brew install --cask google-chrome` の違いは何ですか？

<details>
<summary>解答（自分で考えてから開いてください）</summary>

**A1.**（例）
- 依存関係を自動で解決してくれる
- コマンド一つでインストール・削除・更新ができる
- インストール済みパッケージを一覧管理でき、環境を把握しやすい

**A2.**
```bash
$ brew install wget
$ wget --version
```

**A3.**
```bash
$ brew update       # Homebrew 自体のリポジトリを更新
$ brew upgrade      # インストール済みパッケージをすべて最新版に更新
```

**A4.**
```bash
$ sudo apt update
$ sudo apt install -y nginx
```

**A5.**
- `brew install git`: コマンドラインツール（CLI）をインストールする。`/opt/homebrew/bin/` などに実行ファイルが置かれる
- `brew install --cask google-chrome`: GUI アプリ（.app）をインストールする。`/Applications/` フォルダに配置される

</details>
