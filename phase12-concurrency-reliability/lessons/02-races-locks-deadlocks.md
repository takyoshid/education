# Lesson 02: race・lock・deadlock

Race conditionは実行順によって結果が変わる欠陥です。典型例はread-modify-writeです。

```text
T1: balanceを100と読む
T2: balanceを100と読む
T1: 80を書く
T2: 70を書く
```

本来50になるべき残高が70になります。個々の代入がatomicでも、業務操作全体はatomicではありません。

## lockの設計

- lockで守るのはコード行ではなく不変条件
- 取得中に外部I/Oを行わない
- 複数lockは全箇所で同じ順序に取得する
- lock範囲を狭める前に正しさを証明する
- timeout付き取得や観測可能性も検討する

## deadlockの4条件

相互排他、保持したまま待機、強制解放不可、循環待ちが同時に成立するとdeadlockが可能です。銀行振替で口座ごとのlockを`from`→`to`順に取ると、A→BとB→Aが循環します。口座ID順に統一すれば循環待ちを破れます。

## 演習

[bank-transfer](../exercises/bank-transfer/)で、同時振替後も総残高が一定で残高が負にならないよう実装してください。単一global lock版と口座lock版を計測し、選択を記録します。
