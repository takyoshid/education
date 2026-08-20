# 演習 05: セキュリティ点検

## 目的

- Docker イメージの脆弱性をスキャンできるようになる（Trivy）
- Secrets の漏洩リスクを確認し、対処できる（git-secrets / trufflehog）
- Dockerfile のセキュリティベストプラクティスを適用する
- GitHub Actions に脆弱性スキャンを組み込む

## 前提条件

- 演習 02〜04 が完了していること
- Homebrew がインストール済み（macOS の場合）

---

## 課題 1: Trivy で Docker イメージをスキャンする

### Trivy とは

Trivy（トリビー）は、Aqua Security が開発するオープンソースの脆弱性スキャナーです。
Docker イメージ、ファイルシステム、Git リポジトリなどの脆弱性を検出できます。

### インストール

```bash
# macOS
brew install aquasecurity/trivy/trivy

# Linux（Ubuntu/Debian）
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# バージョン確認
trivy --version
```

### 1-1. 演習 02 のイメージをスキャンする

```bash
# 先にイメージをビルドしておく
cd my-app
docker build -t my-fastapi-app .

# イメージをスキャン
trivy image my-fastapi-app
```

**確認すること**

- `CRITICAL`（深刻）や `HIGH`（高）の脆弱性は何件ありますか？
- どのパッケージに脆弱性がありますか？

### 1-2. ベースイメージを変えてスキャン結果を比較する

```bash
# python:3.12（フルイメージ）をスキャン
trivy image python:3.12

# python:3.12-slim をスキャン
trivy image python:3.12-slim

# 結果を比較
```

**考察**: slim イメージのほうが脆弱性が少ない理由を説明してください。

### 1-3. CRITICAL のみをフィルタして表示する

```bash
trivy image --severity CRITICAL my-fastapi-app
```

### 1-4. スキャン結果を JSON に出力する

```bash
trivy image --format json --output trivy-report.json my-fastapi-app

# 概要を確認
cat trivy-report.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for result in data.get('Results', []):
    vulns = result.get('Vulnerabilities', [])
    if vulns:
        print(f'Target: {result[\"Target\"]}')
        for v in vulns[:3]:
            print(f'  [{v[\"Severity\"]}] {v[\"VulnerabilityID\"]} - {v[\"PkgName\"]}')
"
```

---

## 課題 2: Secrets の漏洩を検出する

### 2-1. .gitignore の確認

まず `.gitignore` が適切に設定されているか確認します。

```bash
cat .gitignore

# 以下が含まれているか確認する
# .env
# .env.*
# *.key
# *.pem
# secrets/
```

### 2-2. Git の履歴に Secrets が入っていないか確認する

```bash
# シークレットと思われるパターンを grep で探す
git log --all -p | grep -E "(password|secret|token|api_key|apikey).*=" | head -20

# .env ファイルが誤ってコミットされていないか
git log --all --full-history -- "*.env"
git log --all --full-history -- ".env"
```

### 2-3. trufflehog でスキャンする（推奨）

trufflehog は Git 履歴から秘密情報のパターンを検出するツールです。

```bash
# macOS
brew install trufflesecurity/trufflehog/trufflehog

# リポジトリをスキャン（ローカル）
trufflehog git file://. --only-verified

# GitHub リポジトリをスキャン
trufflehog github --repo https://github.com/<your-username>/<repo-name>
```

**もし Secrets が検出された場合の対処法**

```bash
# 1. 該当の Secrets をすぐに無効化する（APIキーを再生成する等）
# 2. git filter-repo で履歴から削除する（インストールが必要）
pip install git-filter-repo
git filter-repo --path .env --invert-paths

# 3. または BFG Repo-Cleaner を使う
# https://rtyley.github.io/bfg-repo-cleaner/

# 4. リモートにフォースプッシュ
git push --force-with-lease
```

---

## 課題 3: Dockerfile のセキュリティを改善する

### 3-1. 問題のある Dockerfile を確認する

以下の Dockerfile には複数のセキュリティ上の問題があります。何が問題か指摘してください。

```dockerfile
# 問題のある Dockerfile（問題を探してください）
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# 問題1: root ユーザーで実行している

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**問題の一覧（考えてから確認してください）**

<details>
<summary>ヒントを見る</summary>

1. `FROM python:3.12` — フルイメージは不必要に大きく、脆弱性が多い
2. `COPY . .` — `.env` や秘密情報がイメージに入る可能性がある（.dockerignore が必要）
3. `root ユーザーで実行` — コンテナが侵害された場合、root 権限でホストに影響する可能性がある
4. `pip install` に `--no-cache-dir` がない — キャッシュがイメージに残りサイズが増える

</details>

### 3-2. セキュアな Dockerfile を書く

以下の改善を施した Dockerfile を作成してください。

**改善点**

1. `python:3.12-slim` を使う
2. `.dockerignore` で不要なファイルを除外する（演習 02 で作成済み）
3. 非 root ユーザーでアプリを実行する
4. `pip install --no-cache-dir` を使う
5. `COPY requirements.txt .` → `pip install` → `COPY . .` の順にする

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 依存関係を先にインストール（キャッシュを活用する）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY app/ ./app/

# 非 root ユーザーを作成して切り替える
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# ビルドして実行
docker build -t my-fastapi-app-secure .
docker run -d -p 8000:8000 --name secure-app my-fastapi-app-secure

# ユーザーを確認
docker exec secure-app whoami  # appuser と表示されるはず

# 動作確認
curl http://localhost:8000/health

# クリーンアップ
docker stop secure-app && docker rm secure-app
```

---

## 課題 4: GitHub Actions に Trivy を組み込む

演習 04 で作成した `.github/workflows/ci.yml` に、
Trivy によるセキュリティスキャンを追加してください。

### ci.yml に追加するジョブ

```yaml
  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image for scanning
        run: docker build -t my-fastapi-app:scan .
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: "my-fastapi-app:scan"
          format: "table"
          exit-code: "1"           # CRITICAL/HIGH が見つかった場合にジョブを失敗させる
          ignore-unfixed: true      # 修正版が存在しない脆弱性は無視する
          severity: "CRITICAL,HIGH"
```

**ポイント**

- `exit-code: "1"` にすると、深刻な脆弱性が見つかった場合に CI が失敗する
- `ignore-unfixed: true` で「まだパッチが出ていない」脆弱性を除外する（0 件にしやすくなる）
- `severity: "CRITICAL,HIGH"` で深刻度フィルタを指定する

---

## 課題 5: 依存関係の脆弱性を確認する（pip-audit）

```bash
# pip-audit をインストール
pip install pip-audit

# 現在の環境（または requirements.txt）をスキャン
pip-audit -r requirements.txt

# JSON 形式で出力
pip-audit -r requirements.txt -f json
```

### GitHub Actions への組み込み

```yaml
- name: Audit Python dependencies
  run: |
    pip install pip-audit
    pip-audit -r requirements.txt
```

---

## セキュリティチェックリスト

今回の演習で学んだ内容をもとに、自分のプロジェクトを点検してください。

```
[ ] .env を .gitignore に追加している
[ ] .env.example はあるが、実際の値は含まれていない
[ ] Dockerfile で非 root ユーザーを使っている
[ ] slim または alpine ベースイメージを使っている
[ ] pip install に --no-cache-dir をつけている
[ ] .dockerignore で .env を除外している
[ ] Trivy スキャンで CRITICAL がゼロである
[ ] git 履歴に Secrets が含まれていない
[ ] GitHub Secrets を使ってシークレットを管理している
```

---

## 確認問題

1. Docker コンテナが `root` で実行されるリスクは何ですか？
   コンテナエスケープ（container escape）という概念と合わせて説明してください。

2. `trivy image --ignore-unfixed` フラグを使うと何が変わりますか？
   このフラグを使うべき場合、使うべきでない場合をそれぞれ挙げてください。

3. `.env` ファイルを誤って `git add` してしまい、コミットしてしまいました。
   `git rm .env && git commit` では解決しない理由を説明してください。
   正しい対処方法を説明してください。

4. pip-audit と Trivy は何が違いますか？それぞれどの層の脆弱性を検出しますか？

---

## 提出物

1. `trivy image my-fastapi-app` の出力結果
2. セキュアな `Dockerfile`（課題 3）
3. `docker exec secure-app whoami` の結果
4. 更新した `.github/workflows/ci.yml`（Trivy スキャンを含む）
5. セキュリティチェックリスト（すべてにチェックが入った状態）

---

## 総仕上げプロジェクトへ

演習 01〜05 が完了したら、`project/` ディレクトリの総仕上げプロジェクトに進んでください。
これまで学んだすべての技術を組み合わせて、本番を意識したデプロイ可能なアプリを完成させます。
