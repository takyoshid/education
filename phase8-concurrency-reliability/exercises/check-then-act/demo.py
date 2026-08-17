"""壊れた実装が「どのくらいの頻度で」壊れるかを測る。

    python3 demo.py

このスクリプトは reserve_safe を実装していなくても動きます。
まずこれを実行して、競合が実在することを自分の目で確認してください。
"""

from concurrent.futures import ThreadPoolExecutor

from inventory import Inventory, reserve_unsafe


def run_trial(stock: int, workers: int) -> tuple[int, int]:
    """在庫 stock に対して workers 人が同時に1つずつ予約する。

    戻り値: (成功した予約数, 最終在庫)
    """
    inventory = Inventory(stock=stock)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: reserve_unsafe(inventory), range(workers)))
    return sum(results), inventory.stock


def main() -> None:
    trials = 200
    stock = 1
    workers = 8

    violations = 0
    worst_stock = 0

    for _ in range(trials):
        succeeded, final_stock = run_trial(stock, workers)
        # 不変条件: 在庫1個に対して成功は1件、最終在庫は0のはず
        if succeeded != stock or final_stock < 0:
            violations += 1
            worst_stock = min(worst_stock, final_stock)

    print(f"試行回数         : {trials}")
    print(f"初期在庫         : {stock}(同時に {workers} スレッドが予約を試みる)")
    print(f"不変条件が破れた回数: {violations} / {trials}")
    print(f"観測した最小の在庫  : {worst_stock}")

    if violations == 0:
        print()
        print("今回はたまたま再現しませんでした。これがこのバグの一番怖いところです。")
        print("workers を増やす、trials を増やす、負荷をかけた状態で再実行してください。")
    else:
        print()
        print(f"在庫が {worst_stock} になりました。存在しない商品を売った状態です。")
        print("これを reserve_safe で修正します。")


if __name__ == "__main__":
    main()
