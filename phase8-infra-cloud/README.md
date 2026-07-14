# Phase 8: インフラ・クラウド・Docker・CI/CD・セキュリティ

## 概要

このフェーズでは、現代のソフトウェア開発において欠かせないインフラ技術を体系的に学びます。
コードを「書く」だけでなく、「動かし続ける」ための知識と実践スキルを身につけることが目標です。

---

## 🌟 旅の始まりに: 何も起きなかった夜 — 史上最大の「見えない勝利」

2000年1月1日午前0時。世界は息を呑んで待っていました。「**Y2K 問題**」— 古いシステムの多くが年を下2桁で管理しており(99 の次は 00)、2000年になった瞬間に金融・電力・交通のシステムが誤動作する恐れがあったのです。

その夜、何が起きたか。**ほぼ何も起きませんでした。** 飛行機は落ちず、銀行は止まらず、新年は静かに明けました。すると世間はこう言い始めます。「なんだ、大騒ぎして。最初から大した問題じゃなかったんだ」。

真実は逆です。その静かな夜は、**世界中の無数のエンジニアが数年がかりで膨大なコードを調査・修正した結果**でした。インフラの仕事には残酷で美しい法則があります — **完璧に成功するほど、何も起きず、誰にも気づかれない。**

この Phase で学ぶサーバー、CI/CD、監視、セキュリティは、その「何も起きない日常」を作る技術です。目立たない。しかし、現代文明はその上に立っています。

## 前提知識

- **Phase 7 修了済み**であること
- Linux の基本コマンド（ls, cd, mkdir, cat, grep 程度）が使えること
- HTTP リクエスト/レスポンスの基本概念を理解していること
- Git によるバージョン管理が使えること

---

## 目安期間

**6週間**（1日 1〜2 時間のペースを想定）

| 週 | 内容 |
|----|------|
| 第1週 | ネットワーク基礎・Linux サーバー基礎（Lesson 01〜02） |
| 第2週 | Docker 入門・Docker Compose（Lesson 03〜04） |
| 第3週 | クラウド基礎・CI/CD（Lesson 05〜06） |
| 第4週 | 可観測性・セキュリティ実践（Lesson 07〜08） |
| 第5週 | パフォーマンス・障害対応（Lesson 09〜10） |
| 第6週 | 演習・総仕上げプロジェクト |

---

## 学習目標

このフェーズを修了すると、以下ができるようになります。

1. TCP/IP、TLS、DNS の仕組みを説明できる
2. SSH でリモートサーバーに接続し、systemd でサービスを管理できる
3. Dockerfile を書き、Docker イメージをビルド・実行できる
4. Docker Compose でアプリ + DB のマルチコンテナ環境を構築できる
5. AWS の主要サービスの役割を説明し、無料枠で試せる
6. GitHub Actions で lint / test / build / deploy のパイプラインを構築できる
7. ログ・メトリクスの考え方を理解し、基本的な監視を設定できる
8. シークレット管理・最小権限・HTTPS 化などのセキュリティ実践ができる
9. キャッシュ・ロードバランサ・スケーリング戦略を説明できる
10. インシデント対応の基本フローとポストモーテムの書き方を理解できる

---

## レッスン一覧

| No. | タイトル | 所要時間の目安 |
|-----|----------|--------------|
| 01 | ネットワークを深く理解する（TCP/IP・TLS・DNS） | 3〜4時間 |
| 02 | Linux サーバー基礎（SSH・systemd・ログ・プロセス管理） | 3〜4時間 |
| 03 | Docker 入門（コンテナ・イメージ・Dockerfile） | 4〜5時間 |
| 04 | Docker Compose とマルチコンテナ構成 | 3〜4時間 |
| 05 | クラウド基礎（IaaS/PaaS/SaaS・AWS 主要サービス） | 3〜4時間 |
| 06 | CI/CD（GitHub Actions パイプライン） | 4〜5時間 |
| 07 | 可観測性（ログ・メトリクス・モニタリング・アラート） | 3〜4時間 |
| 08 | セキュリティ実践（シークレット管理・最小権限・HTTPS） | 4〜5時間 |
| 09 | パフォーマンスとスケーリング（キャッシュ・LB・スケール戦略） | 3〜4時間 |
| 10 | 障害対応入門（インシデント対応・ポストモーテム） | 2〜3時間 |

---

## 演習一覧

| ファイル | 内容 |
|----------|------|
| exercises/01-network-basics.md | TCP ハンドシェイクの観察・curl で TLS を確認 |
| exercises/02-linux-server.md | systemd サービスの作成・ログ調査 |
| exercises/03-dockerfile.md | Node.js アプリの Dockerfile 作成 |
| exercises/04-compose.md | アプリ + PostgreSQL の Compose 構成 |
| exercises/05-cloud-setup.md | AWS 無料枠でサーバーを立ち上げる |
| exercises/06-github-actions.md | CI/CD パイプラインの構築 |
| exercises/07-observability.md | ログ収集・Prometheus + Grafana のセットアップ |
| exercises/08-security.md | シークレット管理・HTTPS 化の実装 |
| exercises/09-performance.md | Redis キャッシュの導入・負荷テスト |
| exercises/10-incident.md | 障害シナリオのロールプレイ・ポストモーテム作成 |

---

## 総仕上げプロジェクト

`project/` ディレクトリに、Phase 6 で作成した API を題材にした総仕上げ課題があります。
Docker 化 → CI/CD 構築 → クラウドデプロイまでを一貫して実践します。

---

## 修了条件チェックリスト

以下をすべて達成したら Phase 8 修了です。

### 知識確認

- [ ] OSI 参照モデルの各層の役割を説明できる
- [ ] TCP の 3-way ハンドシェイクを図示できる
- [ ] TLS 証明書の仕組み（CA、証明書チェーン）を説明できる
- [ ] DNS 解決の流れ（再帰リゾルバ・権威 DNS）を説明できる
- [ ] systemd の Unit ファイルの基本構造を書ける
- [ ] コンテナと仮想マシンの違いを説明できる
- [ ] Dockerfile の主要命令（FROM、RUN、COPY、CMD、ENTRYPOINT）を説明できる
- [ ] Docker Compose の volumes / networks の役割を説明できる
- [ ] IaaS / PaaS / SaaS の違いを具体例とともに説明できる
- [ ] GitHub Actions の workflow / job / step の構造を説明できる
- [ ] ログ・メトリクス・トレースの違いを説明できる
- [ ] OWASP Top 10 の上位項目を 3 つ以上説明できる
- [ ] 水平スケール vs 垂直スケールのトレードオフを説明できる
- [ ] インシデント対応の 5 フェーズ（検知→対応→解決→振り返り→改善）を説明できる

### 実技確認

- [ ] 任意のアプリケーションの Dockerfile を書いてビルドできる
- [ ] Docker Compose でアプリ + DB を起動し、接続確認できる
- [ ] GitHub Actions で PR 時に自動テストが走るよう設定できる
- [ ] 環境変数をコード中にハードコードせず、シークレット管理できる
- [ ] Let's Encrypt などで HTTPS 化を実施できる（またはローカルで mkcert を使える）
- [ ] 総仕上げプロジェクトを完成させ、動作確認できる

---

## 環境準備

以下のツールをインストールしておいてください。すべて無料です。

```bash
# Docker Desktop (Mac/Windows) または Docker Engine (Linux)
# https://docs.docker.com/get-docker/

# Docker のバージョン確認
docker --version
docker compose version

# Git
git --version

# curl（通常プリインストール済み）
curl --version
```

---

## 参考資料

- [Docker 公式ドキュメント](https://docs.docker.com/)
- [GitHub Actions 公式ドキュメント](https://docs.github.com/ja/actions)
- [AWS 無料利用枠](https://aws.amazon.com/jp/free/)
- [Let's Encrypt](https://letsencrypt.org/ja/)
- [OWASP](https://owasp.org/)
