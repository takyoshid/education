# Lesson 02: Linux サーバー基礎

## 学習目標

- SSH でリモートサーバーに安全に接続できる
- systemd でサービスを管理できる
- ログの場所を知り、調査できる
- プロセス管理の基本操作ができる

---

## 1. SSH（Secure Shell）

### SSH とは

**SSH（Secure Shell）** は、ネットワーク越しに別のコンピュータへ安全にログインするためのプロトコルです。
通信内容は TLS 同様に暗号化されます。

### SSH 鍵認証の仕組み

パスワード認証より安全な方法として「公開鍵認証」が使われます。

```
[自分のPC]                  [リモートサーバー]
 秘密鍵 (private key)  ←→   公開鍵 (public key)
 ~/.ssh/id_ed25519           ~/.ssh/authorized_keys に登録
```

仕組みのポイント：
- **公開鍵**: サーバーに置いておく。流出しても問題ない
- **秘密鍵**: 手元にだけ保存。絶対に外部に漏らさない

### SSH 鍵の生成と設定

```bash
# 鍵ペアを生成（Ed25519 アルゴリズムを推奨）
ssh-keygen -t ed25519 -C "your-email@example.com"
# 保存場所: ~/.ssh/id_ed25519（秘密鍵）、~/.ssh/id_ed25519.pub（公開鍵）

# 公開鍵の内容を確認
cat ~/.ssh/id_ed25519.pub

# リモートサーバーに公開鍵を転送
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server-ip

# または手動でサーバー側に追記
# cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys（サーバー側で実行）
```

### SSH 接続と基本操作

```bash
# 基本的な接続
ssh user@192.168.1.100

# ポートを指定（デフォルトは 22）
ssh -p 2222 user@192.168.1.100

# 鍵ファイルを明示的に指定
ssh -i ~/.ssh/id_ed25519 user@192.168.1.100

# コマンドをリモートで実行して終了
ssh user@192.168.1.100 "ls -la /var/log"

# ファイルをコピー（scp: secure copy）
scp localfile.txt user@192.168.1.100:/home/user/
scp -r ./myproject user@192.168.1.100:/home/user/

# 双方向ファイル転送（rsync）
rsync -avz ./myproject user@192.168.1.100:/home/user/
```

### SSH 設定ファイル（~/.ssh/config）

接続先を設定ファイルに書いておくと便利です。

```
# ~/.ssh/config

Host myserver
    HostName 192.168.1.100
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host staging
    HostName 10.0.0.50
    User deploy
    IdentityFile ~/.ssh/id_ed25519
```

設定後は `ssh myserver` だけで接続できます。

---

## 2. Linux の基本操作（復習と深化）

### ファイルシステムの主要ディレクトリ

```
/
├── bin/        → 基本コマンド（ls, cat など）
├── etc/        → 設定ファイル
├── home/       → ユーザーのホームディレクトリ
├── var/
│   ├── log/    → ログファイル
│   └── www/    → Web コンテンツ（慣習）
├── usr/
│   ├── bin/    → ユーザーコマンド
│   └── local/  → 手動インストールしたソフトウェア
├── tmp/        → 一時ファイル（再起動で消える）
├── proc/       → プロセス情報（仮想ファイルシステム）
└── sys/        → カーネル・デバイス情報（仮想ファイルシステム）
```

### ファイル権限（パーミッション）

```bash
ls -la /var/log/syslog
# -rw-r--r-- 1 syslog adm 12345 Jul 1 10:00 syslog
#  ^^^                       ^^^
#  rw- : オーナー（読み・書き）
#     r-- : グループ（読みのみ）
#        r-- : その他（読みのみ）

# 権限を変更
chmod 755 script.sh   # rwxr-xr-x
chmod 600 secret.key  # rw-------（秘密鍵のパーミッションはこれが必須）

# オーナーを変更
chown user:group file.txt
sudo chown -R www-data:www-data /var/www/html
```

### パッケージ管理

```bash
# Ubuntu/Debian 系
sudo apt update              # パッケージリストを更新
sudo apt install nginx       # インストール
sudo apt remove nginx        # 削除
sudo apt upgrade             # 全パッケージを更新

# Amazon Linux / CentOS / RHEL 系
sudo yum update
sudo yum install nginx
sudo dnf install nginx  # 新しいバージョンの yum
```

---

## 3. systemd によるサービス管理

### systemd とは

**systemd** は Linux の「init システム」です。
OS 起動時にプロセスを立ち上げ、サービスのライフサイクルを管理します。

```
OS 起動
  └── カーネル
       └── systemd（PID 1）
            ├── sshd（SSH サーバー）
            ├── nginx（Web サーバー）
            ├── postgresql（DB）
            └── ... 他のサービス
```

### systemctl コマンド

```bash
# サービスの状態確認
sudo systemctl status nginx

# サービスの起動・停止・再起動
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx   # 設定ファイルのリロード（プロセスは継続）

# OS 起動時に自動起動するよう設定
sudo systemctl enable nginx
sudo systemctl disable nginx  # 自動起動を無効化

# 起動中のサービス一覧
systemctl list-units --type=service --state=running

# 失敗したサービスを確認
systemctl list-units --state=failed
```

### 自作 systemd Unit ファイルの作成

アプリケーションをサービスとして登録する方法です。

```ini
# /etc/systemd/system/myapp.service

[Unit]
Description=My Node.js Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/myapp
ExecStart=/usr/bin/node /home/ubuntu/myapp/index.js
Restart=on-failure
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3000
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=myapp

[Install]
WantedBy=multi-user.target
```

```bash
# Unit ファイルを作成後、systemd に反映
sudo systemctl daemon-reload

# サービスを有効化して起動
sudo systemctl enable myapp
sudo systemctl start myapp

# 状態確認
sudo systemctl status myapp
```

---

## 4. ログ管理

### ログの場所

```
/var/log/
├── syslog          → システム全体のログ（Ubuntu）
├── messages        → システム全体のログ（CentOS/RHEL）
├── auth.log        → 認証ログ（sudo、SSH ログイン）
├── kern.log        → カーネルログ
├── nginx/
│   ├── access.log  → Nginx アクセスログ
│   └── error.log   → Nginx エラーログ
├── mysql/
│   └── error.log   → MySQL エラーログ
└── apt/            → パッケージ管理のログ
```

### journalctl（systemd のログ管理）

systemd を使うシステムでは、`journalctl` でログを一元管理できます。

```bash
# 最新ログを表示（全サービス）
journalctl -e

# 特定サービスのログ
journalctl -u nginx
journalctl -u myapp

# リアルタイムでログを追う（-f: follow）
journalctl -f
journalctl -u myapp -f

# 時間でフィルタリング
journalctl --since "2024-01-01 00:00:00" --until "2024-01-02 00:00:00"
journalctl --since "1 hour ago"

# ログレベルでフィルタリング（0=emerg, 3=err, 6=info, 7=debug）
journalctl -p err -u nginx

# JSON 形式で出力
journalctl -u myapp -o json | head
```

### tail, grep, awk でのログ解析

```bash
# 最新 100 行を表示
tail -100 /var/log/nginx/access.log

# リアルタイムで追跡
tail -f /var/log/nginx/access.log

# エラーログから特定のパターンを抽出
grep "ERROR" /var/log/myapp/app.log

# 最新 1000 行の中から 500 エラーを探す
tail -1000 /var/log/nginx/access.log | grep " 500 "

# IP アドレスごとのアクセス数を集計
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head 20
```

### ログローテーション（logrotate）

ログファイルが無制限に大きくなるのを防ぐ仕組みです。

```bash
# 設定ファイル例
cat /etc/logrotate.d/nginx
```

```
/var/log/nginx/*.log {
    daily           # 毎日ローテーション
    missingok       # ファイルがなくてもエラーにしない
    rotate 52       # 52 世代分保存
    compress        # gzip 圧縮
    delaycompress   # 直前のローテーションは圧縮しない
    notifempty      # ファイルが空なら処理しない
    create 0640 www-data adm  # 新しいファイルのパーミッション
    sharedscripts
    postrotate
        nginx -s reopen  # Nginx にログファイルを再オープンさせる
    endscript
}
```

---

## 5. プロセス管理

### プロセスの確認

```bash
# 実行中のプロセスを一覧表示
ps aux

# CPU・メモリ使用率でリアルタイム表示
top
htop  # top の高機能版（別途インストール必要）

# 特定のプロセスを検索
ps aux | grep nginx
pgrep nginx          # PID だけ返す

# プロセスツリーを表示
pstree -p
```

### プロセスの終了

```bash
# シグナルを送信してプロセスを終了
kill 1234            # PID 1234 を終了（SIGTERM: 正常終了を要求）
kill -9 1234         # 強制終了（SIGKILL: 問答無用で終了）
kill -HUP 1234       # 設定ファイルの再読み込みを要求（SIGHUP）

# プロセス名で終了
pkill nginx
killall nginx
```

### リソース監視

```bash
# ディスク使用量
df -h               # ファイルシステムごとの使用量
du -sh /var/log     # ディレクトリの合計サイズ
du -sh /var/log/* | sort -h | tail 10  # 大きいディレクトリを探す

# メモリ使用量
free -h

# CPU・ロードアベレージ
uptime
cat /proc/loadavg

# ネットワーク接続状態
ss -tlnp            # リッスン中のポートを確認
ss -tp              # 確立済み接続を確認
```

---

## 6. 環境変数

### 環境変数の基本

```bash
# 確認
echo $HOME
echo $PATH
printenv           # すべての環境変数を表示

# 設定（現在のシェルのみ）
export MY_VAR="hello"
echo $MY_VAR

# 永続化（~/.bashrc または ~/.profile に追記）
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc
```

### .env ファイル

開発では `.env` ファイルで環境変数を管理することが多いです。

```bash
# .env ファイルの例
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
API_KEY=secret123
NODE_ENV=development
```

```bash
# .env を読み込んでコマンドを実行
export $(cat .env | xargs) && node index.js

# .env は必ず .gitignore に追加すること！
echo ".env" >> .gitignore
```

---

## まとめ

| 概念 | 要点 |
|------|------|
| SSH | 公開鍵認証でリモートサーバーに安全接続。秘密鍵は手元だけに保管 |
| ファイル権限 | `chmod` で読み・書き・実行の権限を制御。秘密鍵は `600` 必須 |
| systemd | サービスのライフサイクルを管理。`systemctl` コマンドで操作 |
| ログ | `/var/log/` 以下に集まる。`journalctl -u サービス名 -f` でリアルタイム確認 |
| プロセス管理 | `ps aux` で一覧、`kill PID` で終了。`-9` は最終手段 |

---

## 確認問題

1. SSH 公開鍵認証の仕組みを説明してください。秘密鍵と公開鍵はそれぞれどこに保存しますか？

2. systemd の Unit ファイルの `[Unit]`、`[Service]`、`[Install]` セクションにはそれぞれ何を書きますか？

3. `journalctl -u nginx -f` コマンドの各オプションの意味を説明してください。

4. Node.js アプリを systemd サービスとして登録する Unit ファイルを書いてください。
   - アプリのパス: `/home/ubuntu/api/index.js`
   - 環境変数: `NODE_ENV=production`, `PORT=3000`
   - 失敗時に自動再起動する設定を含めること

5. ディスク使用量が 90% を超えた際、どのコマンドで原因を調査しますか？

---

## 次のレッスン

Lesson 03 では、Docker の基本概念と Dockerfile の書き方を学びます。
