# 演習 05 参考解答: セキュリティ点検

演習 05 の各課題について、期待される実行結果・考え方・解説を示します。
必ず自分でコマンドを実行してから参照してください。

---

## 課題 1: Trivy で Docker イメージをスキャンする

### 1-1. イメージのスキャン結果

```bash
docker build -t my-fastapi-app .
trivy image my-fastapi-app
```

実行結果例:

```
2025-07-06T10:00:00.000+0900    INFO    Vulnerability scanning is enabled
2025-07-06T10:00:00.000+0900    INFO    [vuln] Updating vulnerability database...

my-fastapi-app (debian 12.6)

Total: 12 (UNKNOWN: 0, LOW: 8, MEDIUM: 3, HIGH: 1, CRITICAL: 0)

┌─────────────────────┬───────────────┬──────────┬────────┬──────────────────┬──────────────────┐
│       Library       │ Vulnerability │ Severity │ Status │ Installed Version│  Fixed Version   │
├─────────────────────┼───────────────┼──────────┼────────┼──────────────────┼──────────────────┤
│ libssl3             │ CVE-2024-xxxx │ HIGH     │ fixed  │ 3.0.9-1          │ 3.0.11-1~deb12u1 │
│ libgnutls30         │ CVE-2024-xxxx │ MEDIUM   │ fixed  │ 3.7.9-2          │ 3.7.9-2+deb12u3  │
└─────────────────────┴───────────────┴──────────┴────────┴──────────────────┴──────────────────┘
```

**解説**

- `CRITICAL` (致命的) や `HIGH` (高) の件数に注目します
- `Status: fixed` とある脆弱性は修正版が存在するため、ベースイメージを更新すれば解消できます
- `Status: will_not_fix` は上流で修正予定がないため、回避策を取るか受け入れを判断します
- スキャン結果の件数は実行時期や Python のバージョン、Debian のパッチ適用状況によって変わります

---

### 1-2. フルイメージと slim イメージの比較

```bash
trivy image python:3.12
trivy image python:3.12-slim
```

比較例:

```
python:3.12      Total: 156 (CRITICAL: 3, HIGH: 18, MEDIUM: 45, LOW: 90)
python:3.12-slim Total:  28 (CRITICAL: 0, HIGH:  4, MEDIUM:  8, LOW: 16)
```

**考察: slim イメージの脆弱性が少ない理由**

`python:3.12` (フルイメージ) は Debian の標準パッケージが多数含まれており、
それぞれのパッケージに潜在的な脆弱性が存在します。

`python:3.12-slim` はアプリの実行に必要な最小限のパッケージのみを含む構成です:

```
フルイメージに含まれるが slim には含まれないもの:
- gcc, make などのビルドツール
- wget, curl などのネットワークツール
- vim, less などのエディタ・表示ツール
- perl, tcl などのスクリプト言語ランタイム
```

**最小権限の原則 (Principle of Least Privilege)**: 必要なものだけをインストールすることで
攻撃面 (Attack Surface) を最小化できます。

---

### 1-3. CRITICAL のみのフィルタ

```bash
trivy image --severity CRITICAL my-fastapi-app
```

実行結果例:

```
my-fastapi-app (debian 12.6)

Total: 0 (CRITICAL: 0)
```

`python:3.12-slim` ベースのイメージでは CRITICAL がゼロになることが多いです。
ゼロを維持することが目標です。

---

### 1-4. JSON 形式での出力

```bash
trivy image --format json --output trivy-report.json my-fastapi-app
```

JSON の構造:

```json
{
  "SchemaVersion": 2,
  "ArtifactName": "my-fastapi-app",
  "Results": [
    {
      "Target": "my-fastapi-app (debian 12.6)",
      "Class": "os-pkgs",
      "Type": "debian",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2024-xxxx",
          "PkgName": "libssl3",
          "Severity": "HIGH",
          "InstalledVersion": "3.0.9-1",
          "FixedVersion": "3.0.11-1~deb12u1",
          "Description": "..."
        }
      ]
    }
  ]
}
```

JSON 出力は CI で脆弱性レポートをアーティファクトとして保存したり、
他のツールと連携する際に便利です。

---

## 課題 2: Secrets の漏洩を検出する

### 2-1. .gitignore の確認

適切な `.gitignore` の最小セット:

```gitignore
# 環境変数ファイル (絶対に Git に入れてはいけない)
.env
.env.*
!.env.example    # .env.example は Git に含めてよい

# 鍵・証明書ファイル
*.key
*.pem
*.p12
*.pfx
secrets/

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
coverage.xml

# macOS
.DS_Store
```

**重要**: `.env.example` はテンプレートとして Git に含め、
`.env` (実際の値を含むファイル) は含めません。

---

### 2-2. Git 履歴に Secrets が入っていないかの確認

```bash
git log --all -p | grep -E "(password|secret|token|api_key|apikey).*=" | head -20
```

**何も出力されなければ安全です。**

もし出力がある場合は、どのコミットで追加されたかを特定します:

```bash
git log --all -S "password" --oneline
```

---

### 2-3. trufflehog によるスキャン

```bash
trufflehog git file://. --only-verified
```

実行結果例 (検出なし):

```
🐷🔑🐷  TruffleHog. Unearth your secrets. 🐷🔑🐷

No secrets detected.
```

実行結果例 (検出あり):

```
Found verified result 🐷🔑
Detector Type: AWS
Detector Name: AWS
Raw result: AKIAIOSFODNN7EXAMPLE
Commit: a3f8c2d
File: config/settings.py
Line: 14
```

**Secrets が検出された場合の対処手順:**

1. **すぐに漏洩した認証情報を無効化する** (AWS キーなら IAM で削除、API キーなら再生成)
   - Git からコードを削除しても、すでに見た人がいる可能性があります
   - 認証情報の無効化が最優先です

2. **Git 履歴から削除する**

```bash
# git filter-repo をインストール
pip install git-filter-repo

# 特定ファイルを履歴から完全削除
git filter-repo --path .env --invert-paths

# または特定の文字列パターンを置換
git filter-repo --replace-text <(echo 'AKIAIOSFODNN7EXAMPLE==>REDACTED')
```

3. **リモートにフォースプッシュする**

```bash
git push --force-with-lease origin main
```

4. **チームに周知する** (他の開発者がローカルにクローンしている場合、再クローンが必要)

---

## 課題 3: Dockerfile のセキュリティ改善

### 問題のある Dockerfile の解説

```dockerfile
# 問題のある Dockerfile
FROM python:3.12          # 問題1: フルイメージ使用
WORKDIR /app
COPY . .                  # 問題2: .dockerignore なし
RUN pip install -r requirements.txt  # 問題3: --no-cache-dir なし
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# 問題4: root ユーザーで実行
```

各問題の詳細:

| 問題 | リスク | 解決策 |
|------|--------|--------|
| フルイメージ (`python:3.12`) | イメージが約 1GB、脆弱性が多い | `python:3.12-slim` を使う |
| `COPY . .` | `.env` や秘密鍵がイメージに含まれる | `.dockerignore` で除外する |
| `pip install` に `--no-cache-dir` なし | pip のキャッシュがイメージに残りサイズが増える | `--no-cache-dir` をつける |
| root ユーザーでの実行 | コンテナが侵害された場合にホストへの影響が大きい | 非 root ユーザーを作成して `USER` で切り替える |

---

### セキュアな Dockerfile の解説

`exercises/solutions/Dockerfile` および `project/Dockerfile` が参考解答です。

```dockerfile
FROM python:3.12-slim

# libpq5: psycopg2-binary が必要とする PostgreSQL クライアントライブラリ
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

`apt-get clean && rm -rf /var/lib/apt/lists/*` の意味:
- `apt-get clean`: ダウンロードした .deb パッケージのキャッシュを削除します
- `rm -rf /var/lib/apt/lists/*`: パッケージリストのキャッシュを削除します
- どちらもイメージの最終サイズを小さくするために重要です
- **同じ `RUN` レイヤー内で実行すること**が重要です (別の `RUN` に分けると意味がありません)

```dockerfile
# 依存関係を先にインストール (キャッシュ活用)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY app/ ./app/
```

`requirements.txt` を先にコピーする理由:
Docker はレイヤーを上から順にビルドし、変更があったレイヤー以降をすべて再実行します。
`requirements.txt` が変わっていなければ `pip install` のレイヤーはキャッシュが使われ、
コードのみの変更の場合は `COPY app/` のレイヤーからビルドが始まるため大幅に高速化できます。

```dockerfile
# 非 root ユーザーを作成して切り替える
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser
```

**非 root ユーザーが重要な理由 (コンテナエスケープのリスク)**

コンテナが root で動いているとき、アプリケーションに脆弱性があった場合:

1. 攻撃者が RCE (Remote Code Execution, リモートコード実行) 脆弱性を悪用する
2. コンテナ内で root 権限を得る
3. Docker の設定ミス (例: `--privileged` フラグ) や Linux カーネルの脆弱性を使って
   コンテナの外 (ホスト OS) に脱出する (これが「コンテナエスケープ」)
4. ホスト OS で root 権限を得て、サーバー全体を掌握される

非 root ユーザーで動かすことで、手順 2〜4 のリスクを大幅に低下させます。

---

### 動作確認

```bash
docker build -t my-fastapi-app-secure .
docker run -d -p 8000:8000 --name secure-app my-fastapi-app-secure

# 実行ユーザーの確認
docker exec secure-app whoami
# 期待する出力: appuser

# プロセスの確認
docker exec secure-app ps aux
# 期待する出力:
# USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
# appuser      1  0.5  0.8  30000 16000 ?        Ss   10:00   0:00 uvicorn app.main:app ...

# クリーンアップ
docker stop secure-app && docker rm secure-app
```

---

## 課題 4: GitHub Actions への Trivy 組み込み

`project/.github/workflows/ci.yml` の `security-scan` ジョブが参考解答です。

```yaml
security-scan:
  name: Security scan (Trivy)
  needs: build
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Build image for scanning
      run: docker build -t task-api:scan .
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: "task-api:scan"
        format: "table"
        exit-code: "1"
        ignore-unfixed: true
        severity: "CRITICAL,HIGH"
```

**各オプションの解説**

| オプション | 説明 |
|-----------|------|
| `exit-code: "1"` | CRITICAL/HIGH が 1 件でも見つかればジョブを失敗させる。CI のゲートになる |
| `ignore-unfixed: true` | まだパッチが公開されていない脆弱性を無視する。ゼロ件を達成しやすくなる |
| `severity: "CRITICAL,HIGH"` | これより低い深刻度 (MEDIUM/LOW) は無視する。重大なものだけに集中できる |

**`ignore-unfixed` を使うべき場合・使うべきでない場合**

使うべき場合:
- CI の `exit-code: "1"` と組み合わせて「今すぐ対処できる脆弱性」のみを対象にする場合
- パッチがまだない脆弱性で CI を止めても対処しようがないため

使うべきでない場合:
- コンプライアンス要件で「修正不可の脆弱性も含めてすべて報告」が求められる場合
- セキュリティ監査のレポート作成時

---

## 課題 5: pip-audit による依存関係の脆弱性確認

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

実行結果例 (脆弱性なし):

```
Found 6 packages
No known vulnerabilities found
```

実行結果例 (脆弱性あり):

```
Found 6 packages
Name       Version ID                  Fix Versions
---------- ------- ------------------- ------------
fastapi    0.100.0 GHSA-xxxx-xxxx-xxxx 0.103.1
```

**Trivy と pip-audit の違い**

| ツール | 検出対象 | 特徴 |
|--------|---------|------|
| Trivy | OS パッケージ (apt) + Python パッケージ + コンテナイメージ全体 | 広範囲。イメージビルド後にスキャンする |
| pip-audit | Python パッケージ (`requirements.txt`) のみ | 軽量・高速。開発中でも実行できる |

**使い分け:**
- `pip-audit`: コーディング中やプッシュ前に素早く確認する
- `Trivy`: CI でビルドしたイメージ全体を最終確認する

---

## 確認問題の解答

### 問 1: Docker コンテナを root で実行するリスク

root で実行している場合の攻撃シナリオ:

1. アプリにコマンドインジェクション脆弱性があるとする
2. 攻撃者が `; rm -rf /app` のようなコマンドを実行し、アプリを破壊できる
3. さらに `--privileged` フラグつきのコンテナや、`/proc/sysrq-trigger` へのアクセスなど、
   カーネルの特定の機能を組み合わせると**コンテナエスケープ** (ホスト OS への脱出) が可能になる

非 root (`appuser`) で実行すると:
- `/etc/passwd` などのシステムファイルの書き換えができない
- 1024 番未満のポートにバインドできない (アプリには不要)
- コンテナエスケープを試みても、権限昇格のステップが増えて難しくなる

---

### 問 2: `trivy image --ignore-unfixed` の効果

このフラグを付けると、**修正バージョンが存在しない脆弱性** がスキャン結果から除外されます。

使うべき場合:
- CI で `exit-code: "1"` を使い、自動でデプロイを止める場合
- 修正不可の脆弱性で CI が永遠に失敗し続けるのを防ぐ

使うべきでない場合:
- すべての既知の脆弱性を把握して監視したい場合
- セキュリティチームへの定期報告書を作成する場合

---

### 問 3: .env をコミットしてしまった場合の対処

**`git rm .env && git commit` だけでは解決しない理由:**

Git は全コミットの**完全な差分履歴**を保存しています。
現在のコミットで `.env` を削除しても、過去のコミット履歴に残っており、
`git checkout <古いコミットのハッシュ> -- .env` で復元できてしまいます。

GitHub などのリモートリポジトリに一度プッシュした場合は、
そのリポジトリにアクセスできる人全員が `.env` の内容を取得できた可能性があります。

**正しい対処方法:**

1. **認証情報を即座に無効化する** (最優先)
   - AWS キー: IAM コンソールで削除
   - API キー: サービスの管理画面で再生成
   - DB パスワード: すぐに変更

2. **履歴から完全削除する**

```bash
pip install git-filter-repo
git filter-repo --path .env --invert-paths
```

3. **リモートにフォースプッシュする**

```bash
git push --force-with-lease origin main
```

4. **今後の漏洩を防ぐ**

```bash
# .gitignore に追加
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: add .env to .gitignore"
```

---

### 問 4: pip-audit と Trivy の違い (再掲・詳細版)

```
コンテナイメージ全体
├── OS 層 (Debian/Alpine)
│   ├── apt パッケージ (openssl, libssl, etc.)   <-- Trivy が検出
│   └── システムライブラリ                         <-- Trivy が検出
└── アプリ層
    ├── Python インタープリタ                       <-- Trivy が検出
    └── Python パッケージ (fastapi, sqlalchemy...) <-- Trivy と pip-audit 両方が検出
```

- **pip-audit** は「アプリ層の Python パッケージ」のみ対象。軽量で高速
- **Trivy** は OS 層を含むイメージ全体を対象。より広範囲をカバー
- 両方を使い、pip-audit で開発中に早期発見し、Trivy で CI の最終確認を行うのが理想です

---

## セキュリティチェックリストの完成形

```
[x] .env を .gitignore に追加している
[x] .env.example はあるが、実際の値は含まれていない
[x] Dockerfile で非 root ユーザーを使っている
[x] slim または alpine ベースイメージを使っている
[x] pip install に --no-cache-dir をつけている
[x] .dockerignore で .env を除外している
[x] Trivy スキャンで CRITICAL がゼロである
[x] git 履歴に Secrets が含まれていない
[x] GitHub Secrets を使ってシークレットを管理している
```

---

## 次のステップ

演習 01〜05 が完了したら `project/` ディレクトリへ進みましょう。
`project/README.md` に、ローカル Docker 実行からクラウドデプロイまでの
ステップバイステップガイドが用意されています。
