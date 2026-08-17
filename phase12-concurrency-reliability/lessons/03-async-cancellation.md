# Lesson 03: async・timeout・cancellation

async taskは待機地点で協調的に制御を渡します。同期I/Oや長いCPU loopをevent loop上で実行すると、全taskが停止します。

## timeoutは失敗ではなく予算

上位処理の残り時間より長いtimeoutを下位呼び出しへ設定してはいけません。全体2秒の要求で、3つの下位処理へ各2秒を順番に許す設計は期限を守れません。

## cancellation

取消は例外として伝播します。広い`except Exception`で握りつぶさず、`finally`で資源を解放します。親処理が失敗したのに子taskだけ残る状態を避け、`TaskGroup`のようにtaskの寿命をscopeへ閉じ込めます。

```python
async with asyncio.TaskGroup() as group:
    user = group.create_task(fetch_user())
    orders = group.create_task(fetch_orders())
```

## 演習

- 1つが失敗したとき兄弟taskが取消されることを記録する
- 取消時にもsemaphoreが解放されることをテストする
- blocking関数を直接呼んだ場合と`asyncio.to_thread`を比較する
