# 演習 03 解説: 条件分岐とループ

## 問題 8: `for...else` とは

Python の `for...else` は他の言語にほぼ存在しない独特の構文です。
`else` ブロックは **`break` によってループが終了しなかった場合のみ**実行されます。

```python
for i in range(2, int(n**0.5) + 1):
    if n % i == 0:
        break          # 割り切れた → else は実行されない
else:
    return True        # 全て割り切れなかった → 素数
```

この構造は「検索の失敗(何も見つからなかった)」を表現するのに最適です。
`else` という名前が紛らわしいですが、実態は「break なし完了時」の処理です。

## 問題 9: コラッツ予想の while ループ

コラッツ予想は「必ず終了する」かどうかが数学的に証明されていません(2024年現在)。
しかし実用的な範囲では全ての正の整数に対して終了します。

```python
while n != 1:
    if n % 2 == 0:
        n //= 2
    else:
        n = 3 * n + 1
    sequence.append(n)
```

`while True: ... if 条件: break` で書くこともできますが、
`while n != 1:` の方が「n が 1 になるまで繰り返す」という意図が明確です。

## 問題 6: 順序を保ちながら重複を除く

```python
# O(n^2) の実装
seen = []
result = []
for item in lst:
    if item not in seen:
        seen.append(item)
        result.append(item)
```

`seen` へのアクセスが O(n) なので全体は O(n^2) です。
`seen` を `set` にすれば O(n) になります(本問題では set 禁止でした)。
実際のコードでは `seen = set()` を使いましょう。
