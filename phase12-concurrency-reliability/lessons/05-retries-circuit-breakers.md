# Lesson 05: retry・backoff・circuit breaker

## 学習目標

- retry してよい失敗と、してはいけない失敗を分類できる
- exponential backoff と jitter が何を解決するか説明できる
- retry が障害を**悪化**させる仕組み(retry storm)を説明できる
- circuit breaker の 3 状態と、導入すべき条件を判断できる
- 時計を注入して、sleep なしで retry をテストできる

---

## 1. retry は障害を消さない — 増幅する

まず、最も大事なことから。

> **retry は失敗を成功に変える魔法ではありません。負荷を増やす行為です。**

依存先が過負荷で 503 を返しているとき、全クライアントが 3 回ずつ retry すれば、**トラフィックは 4 倍**になります。回復しかけたサーバーは、再び押し潰されます。

```
通常時:        [■■■■] 100 req/s  → 正常
過負荷:        [■■■■■■■■] 200 req/s → 一部が失敗
retry (3回):   [■■■■■■■■■■■■■■■■] 800 req/s → 完全に停止
                                        ↑ retry が止めを刺した
```

さらに悪いのは、この増幅が**多段で起きる**ことです。

```
ユーザー → API Gateway → 注文サービス → 在庫サービス → DB
             (3回retry)    (3回retry)     (3回retry)

DB への負荷 = 3 × 3 × 3 = 27 倍
```

各層のエンジニアは「念のため 3 回だけ」と思っています。**掛け算になることに誰も気づいていません。**

> **原則**: retry は**1 か所だけ**で行う。多層で retry しない。どの層で行うかをチームで決めて文書化する。

---

## 2. retry してよい失敗の分類

判断基準は 2 つです。**(a) 再試行で直る見込みがあるか**、**(b) 副作用が重複しても安全か**。

| 状況 | 判断 | 理由 |
|---|---|---|
| 接続タイムアウト、接続リセット | **retry する** | 一時的な可能性が高い |
| 429 Too Many Requests | **retry する** | ただし `Retry-After` に従う |
| 503 Service Unavailable | **retry する** | 一時的な過負荷 |
| 500 Internal Server Error | **条件付き** | 相手のバグなら何度やっても同じ |
| 502, 504 (Gateway 系) | **条件付き** | **副作用が実行済みかもしれない** |
| 400 Bad Request | retry しない | リクエストが悪い。何度でも失敗する |
| 401 / 403 | retry しない | 認証・認可の問題 |
| 404 Not Found | retry しない | 存在しない |
| 409 Conflict | retry しない | 状態が競合している。読み直しが必要 |
| 422 Validation Error | retry しない | 入力が悪い |

### 最も危険なケース: timeout と 504

```
クライアント                     サーバー
    │──── POST /charge ────────▶│
    │                            │ 課金を実行 ✓
    │ (5秒経過 → timeout)        │
    │◀────────╳ 応答が届かない   │
  「失敗した」                「成功した」
```

**timeout は「失敗した」ことを意味しません。「結果が分からない」ことを意味します。**

ここで無条件に retry すると、二重課金です。Lesson 04 の二将軍問題そのものです。

> **鉄則**: **冪等でない操作を、冪等性の仕組みなしに retry してはいけません。**
> POST を retry したいなら、まず idempotency key を実装してください。順序が逆です。

```python
# ✗ 危険
for attempt in range(3):
    try:
        return requests.post("/charge", json=payload, timeout=5)
    except requests.Timeout:
        continue          # 課金済みかもしれないのに再送している

# ○ 冪等性を先に確保する
key = str(uuid.uuid4())   # 再試行しても同じ key を使う
for attempt in range(3):
    try:
        return requests.post(
            "/charge", json=payload, timeout=5,
            headers={"Idempotency-Key": key},
        )
    except requests.Timeout:
        continue
```

---

## 3. exponential backoff と jitter

### 固定間隔の問題

```python
for attempt in range(5):
    try:
        return call()
    except TransientError:
        time.sleep(1)     # ✗ 毎回1秒
```

相手が回復するのに 30 秒かかるなら、1 秒間隔の再試行は**ただの追い打ち**です。

### exponential backoff — 待ち時間を指数的に増やす

```python
delay = base * (2 ** attempt)
# base=0.1 の場合: 0.1s → 0.2s → 0.4s → 0.8s → 1.6s
```

相手が回復するまで、こちらは静かになっていきます。

### jitter — 同期を崩す

exponential backoff だけでは、まだ問題が残ります。**全クライアントが同じタイミングで再試行する**のです。

```
障害発生 ↓
クライアント1: ×    待機    ×    待機      ×
クライアント2: ×    待機    ×    待機      ×
クライアント3: ×    待機    ×    待機      ×
                    ↑        ↑           ↑
                 全員が同時に殺到する (thundering herd)
```

障害はたいてい全クライアントに同時に起きるので、再試行のタイミングも揃います。回復した瞬間に全員が同時に押し寄せ、また落ちます。

**jitter (ゆらぎ)** は待ち時間にランダム性を加えて、この同期を崩します。

```python
import random

# full jitter (推奨): 0 〜 上限 の一様乱数
delay = random.uniform(0, min(cap, base * (2 ** attempt)))
```

```
jitter あり
クライアント1: ×  待機   ×      待機        ×
クライアント2: ×      待機    ×    待機   ×
クライアント3: ×   待機      ×        待機   ×
                    ↑ ばらける。負荷が平準化される
```

### 実装

```python
import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry_with_backoff(
    func: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 0.1,
    cap: float = 10.0,
    deadline: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    rand: Callable[[float, float], float] = random.uniform,
) -> T:
    """一時的な失敗を exponential backoff + full jitter で再試行する。

    sleep / monotonic / rand を引数で受け取っているのはテストのため。
    偽物を注入すれば、実際に待つことなく待機時間を検証できる。
    """
    started = monotonic()

    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError:
            is_last = attempt == max_attempts - 1
            if is_last:
                raise

            delay = rand(0, min(cap, base_delay * (2 ** attempt)))

            # 回数だけでなく「締め切り」も見る。
            # 上位の予算を超えてまで retry しても意味がない (Lesson 03)。
            if deadline is not None and monotonic() - started + delay > deadline:
                raise

            sleep(delay)

    raise AssertionError("到達しない")
```

### 回数だけでなく deadline を持つ

`max_attempts=5` だけでは、最悪の待ち時間が読めません。上位が「2 秒以内に応答する」予算を持っているなら、retry もその中に収まらなければ意味がありません。**回数と締め切りの両方**を設定してください。

---

## 4. テストのために時計を注入する

`time.sleep()` を直接呼ぶコードは、テストに実時間がかかります。5 回の retry を検証するのに 30 秒待つテストは、誰も実行しなくなります。

**解決策は、時計とスリープを引数で受け取ることです。**

```python
class FakeClock:
    """時間を自分で進められる偽の時計"""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds      # 実際には待たず、時計だけ進める


def test_backoff_grows_exponentially():
    clock = FakeClock()
    calls = []

    def always_fails():
        calls.append(1)
        raise TransientError()

    with pytest.raises(TransientError):
        retry_with_backoff(
            always_fails,
            max_attempts=4,
            base_delay=1.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
            rand=lambda lo, hi: hi,   # jitter を無効化して上限を決定的に見る
        )

    assert len(calls) == 4
    assert clock.slept == [1.0, 2.0, 4.0]   # 一瞬で検証できる
```

**乱数も注入します。** `rand=lambda lo, hi: hi` とすれば jitter の上限が、`lambda lo, hi: lo` とすれば下限がテストできます。「ランダムだからテストできない」は誤りです。

これは Lesson 03 で見た「グローバルな状態を関数の中で直接読まない」の応用であり、Phase 7 の依存性注入と同じ考え方です。

---

## 5. circuit breaker

retry は「相手がすぐ回復する」前提です。相手が**長時間ダウンしている**なら、retry は無駄な待ち時間とリソース消費を生むだけです。

**circuit breaker (サーキットブレーカー)** は、失敗が続く依存先への呼び出しを**一時的に遮断**します。名前のとおり、電気のブレーカーと同じ発想です。

### 3 つの状態

```
        失敗が閾値を超えた
   ┌──────────────────────────┐
   │                          ▼
┌─────────┐            ┌──────────┐
│ CLOSED  │            │   OPEN   │
│ 通常通り │            │ 即座に失敗 │
│ 通す     │            │ 呼ばない   │
└─────────┘            └──────────┘
   ▲                          │
   │ 成功            一定時間経過 │
   │                          ▼
   │                  ┌──────────────┐
   └──────────────────│  HALF-OPEN   │
                      │ 少数だけ試す   │
        失敗 ─────────│              │
          └──────────▶└──────────────┘
```

| 状態 | 挙動 |
|---|---|
| **CLOSED** | 通常。呼び出しを通し、失敗率を記録する |
| **OPEN** | **呼び出さずに即座に失敗を返す**。相手に負荷をかけない |
| **HALF-OPEN** | 一定時間後、少数のリクエストだけ通して回復を確認する |

### なぜ「即座に失敗する」ことに価値があるのか

依存先が落ちているとき、timeout を待ってから失敗するのと、待たずに失敗するのとでは大きな差があります。

```
circuit breaker なし:
  リクエスト1: [5秒待つ] → 失敗   ← スレッド/接続を5秒占有
  リクエスト2: [5秒待つ] → 失敗
  ...
  → スレッドプールが枯渇し、無関係な機能まで応答不能になる (カスケード障害)

circuit breaker あり (OPEN):
  リクエスト1: 即座に失敗 → フォールバック表示
  リクエスト2: 即座に失敗 → フォールバック表示
  → 自分は生き残る。相手にも余計な負荷をかけない
```

**circuit breaker が守るのは相手ではなく、自分です。** 障害を「相手のサービスの一部機能の劣化」に留め、システム全体の停止を防ぎます。

### 導入前に必要なもの

circuit breaker は魔法ではありません。導入には前提があります。

1. **失敗率を観測できること**(Phase 8 の可観測性)
2. **閾値と回復条件を決められること**(何%の失敗で開くか、何秒で試すか)
3. **OPEN のときに何を返すか決まっていること** — ここが最も重要

3 番目を決めずに導入すると、ただエラーが速く返るだけになります。

| フォールバック戦略 | 例 |
|---|---|
| キャッシュされた古い値を返す | 「10分前の在庫数」を表示 |
| 縮退した機能を返す | おすすめ欄を隠して本体は表示 |
| 明示的にエラーを返す | 「決済は現在利用できません」 |

**「レコメンドが出ないが商品は買える」は成功です。「レコメンドの障害で全ページが落ちる」が失敗です。**

---

## 💡 コラム: 再ミラーリングの嵐 — retry がクラウドを止めた日

2011年4月21日、AWS の米国東部リージョンで大規模障害が発生しました。Reddit、Quora、Foursquare、Hootsuite など多数のサービスが停止し、完全復旧まで**約4日**を要しました。当時のクラウド史上、最も広く知られた障害です。

きっかけは、ネットワーク構成変更の際の操作ミスでした。EBS(ブロックストレージ)クラスタのトラフィックが、本来の高帯域ネットワークではなく、**冗長用の低帯域ネットワークへ誤って向けられた**のです。

ここまでは、よくある人的ミスです。問題はその後に起きたことでした。

EBS のボリュームは、データを複数ノードにミラーリングして冗長性を保っています。ノードは自分のミラー相手を見失うと、「データが危険な状態にある」と判断し、**新しいミラー先を探して複製を開始**します。これは正常時には正しい自己修復の仕組みです。

しかしこのとき、ネットワークが細くなったせいで**大量のノードが同時にミラー相手を見失いました**。すべてのノードが一斉に、新しい複製先を探し始めます。

- 複製が空きスペースを食い潰す
- 空きが無いので複製に失敗する
- 失敗したのでまた別の複製先を探す
- その探索自体がネットワークとサーバーを飽和させる
- さらに多くのノードがミラーを見失う

AWS はこれを「**re-mirroring storm(再ミラーリングの嵐)**」と呼びました。ネットワークを元に戻した後も、**嵐は自力で止まりませんでした**。システムが自分自身の回復動作によって、自分を殺し続けていたのです。復旧には、容量を追加し、複製処理を手動で抑制するという地道な作業が必要でした。

この障害から業界が学んだ教訓は、そのまま現代の設計原則になっています。

- **自己修復のロジックには、必ず上限と抑制を入れる。** 「危険を検知したら全力で修復する」は、全員が同時にやると攻撃になります。
- **backoff と jitter は飾りではない。** 一斉に動くことこそが危険なのです。
- **回復動作は、平常時の負荷ではなく障害時の負荷で設計する。** 障害時にはあらゆる再試行が同時に走ります。

Netflix はこの時代の教訓から **Hystrix** を開発し、circuit breaker、バルクヘッド、フォールバックといったパターンを業界に広めました。「依存先は落ちる。落ちたときに自分まで道連れにならない設計をせよ」という思想です。

`time.sleep(1)` を `random.uniform(0, 2 ** attempt)` に書き換えるのは、たった一行の変更です。しかしそれは、2011年の4日間から人類が学んだことの結晶です。

---

## まとめ

- **retry は負荷を増やす**。多層で retry すると掛け算になる。retry は 1 か所だけで行う
- **timeout は「失敗」ではなく「結果不明」**。冪等性なしに retry してはいけない
- 4xx は原則 retry しない。429 / 503 / 接続エラーは retry 候補
- **exponential backoff** で相手に回復の余地を与え、**jitter** で thundering herd を防ぐ
- 回数だけでなく **deadline** を持つ。上位の予算を超えない
- **時計・sleep・乱数を注入**すれば、待たずに retry をテストできる
- **circuit breaker は自分を守る仕組み**。OPEN 時に何を返すかを決めてから導入する

---

## 確認問題

1. 3 層のサービスがそれぞれ「念のため 3 回」retry すると、最下層への負荷は何倍になりますか。
2. POST リクエストが timeout しました。retry してよいですか。判断に必要な情報は何ですか。
3. exponential backoff だけでは不十分な理由と、jitter が解決する問題を説明してください。
4. `max_attempts` だけでなく `deadline` も必要なのはなぜですか。
5. `time.sleep()` を直接呼ぶ retry 関数の、テスト上の問題は何ですか。どう設計を変えますか。
6. circuit breaker の 3 状態を挙げ、HALF-OPEN が必要な理由を説明してください。
7. 「circuit breaker は相手ではなく自分を守る」とはどういう意味ですか。
8. あなたのシステムの外部依存を 1 つ選び、それが 10 分間ダウンしたときに何を返すべきか決めてください。

---

## 演習

[`exercises/retry-backoff/`](../exercises/retry-backoff/) で、**sleep せずに** retry をテストします。

実装するもの:

- 注入可能な `sleep` / `monotonic` / `rand` を持つ retry 関数
- 再試行対象の例外の分類

テストで証明すること:

- 待機時間が指数的に増える(乱数を固定して決定的に検証)
- retry しない例外は 1 回で終わる
- deadline を超える場合、待機せずに諦める
- **テスト全体が 1 秒以内に終わる**

最後の条件が重要です。実時間を待つテストを書いた時点で、そのテストは CI で嫌われ、やがて消されます。
