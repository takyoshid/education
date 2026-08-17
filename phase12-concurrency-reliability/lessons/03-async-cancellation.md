# Lesson 03: async・timeout・cancellation

## 学習目標

- イベントループをブロックする書き方を見分け、回避できる
- timeout を「予算 (budget)」として設計できる
- 取消 (cancellation) が例外として伝播することを理解し、資源を確実に解放できる
- `TaskGroup` でタスクの寿命をスコープに閉じ込められる

---

## 1. 協調的マルチタスク — 譲らないタスクは全体を止める

async は**協調的 (cooperative)** です。OS が強制的に切り替えるスレッドと違い、**タスク自身が `await` で制御を譲って初めて**他のタスクが動きます。

```
正常: await のたびに制御が戻る
  タスクA: ──await──┐        ┌──await──┐
  タスクB:          └────────┘         └──────
           ループが回り続ける

異常: 譲らないタスクが1つあると全部止まる
  タスクA: ────────────────────────────  (time.sleep(10))
  タスクB: (待ち)                        ← 10秒間まったく動けない
```

つまり、**1 つのタスクの不注意が、無関係な全リクエストを巻き添えにします**。スレッドなら OS が強制的に切り替えるので、ここまでの被害にはなりません。

### イベントループを止める書き方

```python
import asyncio, time
import requests

async def handler():
    time.sleep(1)                      # ✗ 同期 sleep。全タスクが1秒止まる
    requests.get("https://example.com")  # ✗ 同期 HTTP。応答まで全タスクが止まる
    total = sum(i * i for i in range(10**8))  # ✗ 長い CPU 計算も同じ
```

正しくはこうです。

```python
import asyncio
import httpx

async def handler():
    await asyncio.sleep(1)                        # ○ 非同期 sleep
    async with httpx.AsyncClient() as client:     # ○ 非同期 HTTP クライアント
        await client.get("https://example.com", timeout=5)
    total = await asyncio.to_thread(heavy_calc)   # ○ CPU 処理は別スレッドへ逃がす
```

**判定法**: そのライブラリのドキュメントに `async def` / `await` が出てこないなら、それは同期ライブラリです。`asyncio.to_thread()` で包むか、非同期対応の別ライブラリを探してください。

| 同期 | 非同期 |
|---|---|
| `requests` | `httpx` / `aiohttp` |
| `psycopg2` | `asyncpg` / `psycopg` (async モード) |
| `time.sleep` | `asyncio.sleep` |
| `open()` | `aiofiles`(または `to_thread`) |

> **デバッグの助け**: `asyncio.run(main(), debug=True)` を使うと、100ms 以上ループをブロックしたコールバックを警告してくれます。開発中は常に有効にしてください。

---

## 2. timeout は「失敗」ではなく「予算」

timeout を「念のため設定する上限」だと考えていると、必ず破綻します。**timeout は使える時間の配分 (budget) です。**

### 悪い例: 予算を超過する設計

ユーザーへの応答目標が 2 秒だとします。

```python
# ✗ 各呼び出しに2秒を許すと、合計6秒かかりうる
user = await fetch_user(timeout=2)
orders = await fetch_orders(timeout=2)
items = await fetch_items(timeout=2)
```

**それぞれは「2秒以内」を守っているのに、全体では守れていません。**

### 良い例: 上位が持つ予算を分配する

```python
import asyncio

async def handle_request() -> dict:
    # 全体の予算は 2 秒。これを超えたら何がどうであれ打ち切る
    async with asyncio.timeout(2.0):
        user = await fetch_user()
        orders = await fetch_orders()
        items = await fetch_items()
    return {"user": user, "orders": orders, "items": items}
```

`asyncio.timeout()` (Python 3.11+) はブロック全体に期限を設けます。内側の処理が何段ネストしていても、**期限は 1 つ**です。

さらに、独立した処理なら並行にすることで予算内に収まります。

```python
async def handle_request() -> dict:
    async with asyncio.timeout(2.0):
        async with asyncio.TaskGroup() as group:
            user_task = group.create_task(fetch_user())
            orders_task = group.create_task(fetch_orders())
            items_task = group.create_task(fetch_items())
    return {
        "user": user_task.result(),
        "orders": orders_task.result(),
        "items": items_task.result(),
    }
```

```
直列 (最悪 6 秒):   [fetch_user 2s][fetch_orders 2s][fetch_items 2s]
並行 (最悪 2 秒):   [fetch_user 2s]
                    [fetch_orders 2s]
                    [fetch_items 2s]
```

### timeout を設定しない = 無限に待つ

**すべての外部呼び出しに timeout を付けてください。例外はありません。**

timeout の無い呼び出しは、相手が沈黙したときに永久に戻ってきません。その間コネクション、スレッド、メモリを掴んだままです。これが積み重なると、**相手の障害があなたのシステムの障害になります**(Lesson 05 の circuit breaker へ続きます)。

```python
requests.get(url)              # ✗ 既定では無限に待つ
requests.get(url, timeout=5)   # ○
httpx.get(url, timeout=5)      # ○ (httpx は既定 5 秒だが明示する)
```

---

## 3. cancellation — 取消は例外としてやってくる

タスクを取り消すと、そのタスクの `await` 地点で `asyncio.CancelledError` が送出されます。

```python
task = asyncio.create_task(long_operation())
await asyncio.sleep(0.1)
task.cancel()                    # 取消を要求する
try:
    await task
except asyncio.CancelledError:
    print("取り消されました")
```

重要なのは、**取消は「即座の停止」ではなく「例外の送出」である**という点です。タスクは次に `await` するまで止まりません。そして例外である以上、`except` で握りつぶせてしまいます。

### やってはいけない: 取消を握りつぶす

```python
# ✗ 取消を無視してしまう
async def worker():
    while True:
        try:
            await process_one()
        except Exception:        # CancelledError は捕まらない…が
            logger.exception("失敗")
            continue
```

Python 3.8 以降、`CancelledError` は `Exception` ではなく **`BaseException`** を継承しているため、上のコードでは**捕まりません**。これは意図的な設計変更です。

しかし `except BaseException:` や、裸の `except:` を書くと握りつぶせてしまいます。

```python
# ✗ 絶対にダメ
try:
    await something()
except BaseException:
    pass                # 取消も、Ctrl-C も、全部無視される
```

### 正しい: `finally` で資源を解放する

```python
async def worker(semaphore: asyncio.Semaphore) -> None:
    await semaphore.acquire()
    try:
        await do_work()
    finally:
        # 取消されても、例外が出ても、必ず解放される
        semaphore.release()
```

**取消はいつでも起こりうる**という前提でコードを書きます。`finally`(または `async with`)を使えば、取消経路でも資源が漏れません。

### 後始末に時間がかかる場合

`finally` の中でさらに `await` すると、その最中にもう一度取消されることがあります。確実にやり切りたい後始末は `asyncio.shield()` で保護します。

```python
async def worker():
    try:
        await do_work()
    finally:
        # 取消中でも、この後始末だけは完了させたい
        await asyncio.shield(cleanup())
```

ただし `shield` を多用すると「取消できないタスク」が増え、graceful shutdown が効かなくなります。**本当に必要な最小限**に留めてください。

---

## 4. TaskGroup — タスクの寿命をスコープに閉じ込める

最も多い async のバグは、**「親が失敗したのに、子タスクだけ生き残る」** ことです。

```python
# ✗ 古い書き方。orphan task が残る
async def handle():
    task1 = asyncio.create_task(fetch_a())
    task2 = asyncio.create_task(fetch_b())
    result1 = await task1        # ここで例外が出ると…
    result2 = await task2        # task2 は回収されないまま残り続ける
```

`task1` が失敗した瞬間に関数を抜けると、`task2` は宙に浮きます。DB 接続を握ったまま、誰も結果を受け取らないまま動き続け、やがて「Task exception was never retrieved」という警告だけが残ります。

`TaskGroup` (Python 3.11+) はこれを構造的に防ぎます。

```python
async def handle() -> tuple:
    async with asyncio.TaskGroup() as group:
        task1 = group.create_task(fetch_a())
        task2 = group.create_task(fetch_b())
    # ここに到達した時点で、両方とも必ず完了している
    return task1.result(), task2.result()
```

`TaskGroup` の保証:

1. `async with` を抜けるとき、**全タスクの完了を待つ**
2. **1 つが失敗したら、兄弟タスクを自動的に取り消す**
3. 例外は `ExceptionGroup` としてまとめて送出される

```
tg = TaskGroup
┌─ async with tg: ─────────────────────┐
│   task1 ████████✗ 失敗               │
│   task2 ██████──取消─╳               │  ← 自動で取り消される
│   task3 ████──取消─╳                 │
└──────────────────────────────────────┘
        ↓ ExceptionGroup が送出される
```

これは **structured concurrency (構造化並行性)** と呼ばれる考え方です。「関数を抜けたらローカル変数が消える」のと同じように、「スコープを抜けたらタスクも終わっている」ことを保証します。

### `ExceptionGroup` の受け取り方

```python
try:
    async with asyncio.TaskGroup() as group:
        group.create_task(fetch_a())
        group.create_task(fetch_b())
except* ValueError as eg:          # except* (star) で型ごとに捕まえる
    print(f"ValueError が {len(eg.exceptions)} 件")
except* TimeoutError as eg:
    print(f"TimeoutError が {len(eg.exceptions)} 件")
```

複数のタスクが**同時に別々の理由で**失敗しうるため、例外も複数になります。`except*` はそれを型ごとに振り分ける構文です。

---

## 5. 並行数を制限する

「全部並行にすれば速い」は誤りです。1000 件のリクエストを一斉に投げれば、相手のサーバーを落とすか、こちらのファイルディスクリプタが枯渇します。

```python
async def fetch_all(urls: list[str], limit: int = 10) -> list:
    semaphore = asyncio.Semaphore(limit)

    async def fetch_one(url: str):
        async with semaphore:            # 同時に limit 個まで
            return await client.get(url, timeout=5)

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(fetch_one(u)) for u in urls]
    return [t.result() for t in tasks]
```

`async with semaphore:` を使えば、取消されても例外が出ても確実に解放されます。`acquire()` / `release()` を手書きするより安全です。

**適切な同時数は計測で決めます。** 相手のレート制限、こちらの CPU、ネットワーク帯域のどれが先に飽和するかは、やってみないと分かりません。

---

## 💡 コラム: 2億キロ先のデッドロックを、地球から直した

1997年7月4日、NASA の探査機 **マーズ・パスファインダー** が火星に着陸しました。小型ローバー「ソジャーナ」を降ろし、鮮明な画像を送り始め、ミッションは大成功に見えました。

数日後、探査機が**勝手に再起動**し始めます。しかも繰り返し。そのたびにその日のデータが失われました。地上のチームは原因が分からず、貴重な観測時間が溶けていきました。

原因は **priority inversion (優先度逆転)** でした。

パスファインダーは VxWorks というリアルタイム OS を使い、共有メモリ領域を mutex で保護していました。そこに 3 つのタスクがいました。

- **高優先度**: 情報バス管理(頻繁に動く必要がある)
- **中優先度**: 通信タスク(そこそこ長く動く)
- **低優先度**: 気象データ収集

事故はこう起きます。低優先度の気象タスクが mutex を取得した直後に、高優先度の情報バスタスクが動き出す。バスタスクは同じ mutex が欲しいので待つ。ここまでは正常です。ところが**そこへ中優先度の通信タスクが割り込む**と、優先度が高いのでプリエンプトして長時間走り続けます。

結果、低優先度タスクは mutex を持ったまま実行機会を得られず、**高優先度タスクは中優先度タスクに間接的にブロックされ続けます**。優先度の順序が事実上逆転しているのです。

そして、パスファインダーには**ウォッチドッグタイマー**が積まれていました。情報バスタスクが一定時間内に動かないと「システムが異常だ」と判断してリセットする仕組みです。ウォッチドッグは正しく仕事をしていました。**再起動は症状であり、原因ではなかった**のです。

JPL のチームは地上に同一構成のテスト機を持っており、トレース機能を有効にして数日回し続け、ついに同じ現象を再現します。原因が分かれば修正は 1 行に近いものでした。mutex 生成時のフラグを変更し、**優先度継承 (priority inheritance)** を有効にする。低優先度タスクが mutex を持っている間だけ、待っている側の優先度を一時的に引き継がせるのです。

チームはこのパッチを、**約2億キロ離れた火星の探査機へ送信**しました。修正は適用され、リセットは止まりました。ミッションは予定を大幅に超えて continued。

このエピソードから持ち帰るべきものは3つあります。

1. **並行バグは「症状」と「原因」が遠く離れる。** 見えていたのは再起動であって、mutex ではありませんでした。
2. **本番と同じ構成の再現環境が、最終的に一番速い。** 推測を何日続けても届かなかった答えに、トレースを取れる環境が届きました。
3. **ウォッチドッグは正しかった。** 壊れた状態で走り続けるより、気づいて止まるほうが良い。これは Lesson 05 の circuit breaker と同じ思想です。

あなたが `asyncio.timeout()` を書くとき、やっているのはパスファインダーのウォッチドッグと同じことです。**「いつまでも待たない」という設計判断**です。

---

## まとめ

- async は協調的。**譲らないタスク 1 つが全体を止める**。同期 I/O と長い CPU 計算をループ上で実行しない
- **timeout は上限ではなく予算**。上位が持つ期限を下位へ分配する。`asyncio.timeout()` でスコープに期限を設ける
- **すべての外部呼び出しに timeout を付ける。例外はない**
- 取消は `CancelledError` として伝播する。`BaseException` 継承なので `except Exception` では捕まらない
- **握りつぶさず、`finally` / `async with` で資源を解放する**
- `TaskGroup` はタスクの寿命をスコープに閉じ込め、失敗時に兄弟を自動で取り消す
- 並行数は `Semaphore` で制限する。適切な値は計測で決める

---

## 確認問題

1. `time.sleep(1)` を async 関数の中で呼ぶと何が起きますか。スレッドで同じことをした場合と比較してください。
2. 「timeout は予算である」とはどういう意味ですか。各呼び出しに個別の timeout を設定する設計の何が問題ですか。
3. `except Exception:` では `CancelledError` が捕まらないのはなぜですか。これは何を守るための設計ですか。
4. `TaskGroup` を使わずに `create_task` した場合に起こりうる問題を 2 つ挙げてください。
5. `asyncio.shield()` はどんなときに使いますか。多用するとどんな害がありますか。
6. 1000 件の URL を取得します。同時実行数をどう決めますか。「全部並行」の何が問題ですか。
7. 手元で使っているライブラリが非同期対応かどうか、どう判定しますか。対応していない場合の選択肢は。

---

## 演習

[`exercises/async-timeout/`](../exercises/async-timeout/) で次を確認します。

- 1 つのタスクが失敗したとき、**兄弟タスクが取り消される**ことをテストで記録する
- 取消されても **semaphore が解放される**ことをテストする
- ブロッキング関数を直接呼んだ場合と `asyncio.to_thread` で包んだ場合の**実測差**を出す

3 番目は必ず自分で計測してください。「ブロックすると遅くなる」と読むのと、目の前で 10 倍の差を見るのとでは、身につき方がまったく違います。
