# 参考解答: リファクタリング後のコード

**注意**: このREADMEは、自分でリファクタリングを試みた後に読むこと。
先に解答を見ると学習効果が大幅に下がる。

---

## コードの読み方

### 依存関係の方向

```
formatters.py
    ↓ (使う)
services.py
    ↓ (使う)
repositories.py  (抽象インターフェース)
    ↓ (実装する)
models.py
```

`services.py` は `repositories.py` の抽象クラスにのみ依存している。
具体的なDB実装(`SQLiteOrderRepository`)を知らない。

### テストの読み方

`tests/test_services.py` を読むと、DIP(依存関係逆転原則)の恩恵が分かる:

```python
# DB なしでサービス層のテストが書ける
product_repo = InMemoryProductRepository(products)
order_repo = InMemoryOrderRepository()
service = OrderService(
    order_repository=order_repo,
    product_repository=product_repo,
    ...
)
```

`InMemoryProductRepository` はメモリ内に商品データを保持するだけのシンプルな実装。
SQLite も PostgreSQL も必要ない。

---

## レガシーコードとの対応表

| legacy/ の問題 | refactored/ での解決 |
|--------------|-------------------|
| `proc()` に全責務が混在 | `services.py` でビジネスロジック、`repositories.py` でDB操作を分離 |
| 魔法のインデックス `row[3]` | `models.py` の dataclass フィールドで名前付きアクセス |
| マジックナンバー `10`, `5000` | 定数 `LOW_STOCK_THRESHOLD`, `FREE_SHIPPING_THRESHOLD` で命名 |
| クーポンの重複 if/elif | `CouponStrategy` (Strategy パターン) で各クーポンをクラス化 |
| メール送信が関数に混在 | `OrderNotifier` インターフェースで切り離し |
| テストにDB・メールサーバーが必要 | InMemory 実装で DB 不要のテスト |
| パスワードハッシュを戻り値に含む | `User` モデルからパスワードハッシュを除外 |

---

## 発見できるコードスメルのリスト

`legacy/` にあるコードスメルを全て挙げる。
自分が発見できたものと照合してみよう。

**`legacy/order_system.py`**
1. 長いメソッド (Long Method): `proc()` が約70行
2. 神関数: バリデーション・在庫確認・割引計算・DB保存・メール送信が1関数
3. マジックナンバー: `5000`(送料無料閾値)、`0.10`(消費税率)、`500`(送料)
4. ハードコードされた認証情報: `SMTP_PASS = "password123"`
5. 魔法のインデックス: `p[2]`、`p[3]`、`o[3]`
6. スイッチ文の重複: クーポンの if/elif が1箇所だが将来重複する設計
7. 略語の命名: `proc`、`itms`、`cpn`、`uid`、`st`、`sh`、`tot`、`oid`
8. エラーの握りつぶし: `except Exception as e: print(...)` でメール失敗を無視

**`legacy/user_manager.py`**
1. 神クラス (God Class): 認証・メール・SMS・レポート・アバターが1クラス
2. 魔法のインデックス: `user[5]`、`user[4]`
3. 外部サービスへの直接依存: `requests.post(SENDGRID_API_KEY, ...)` がクラス内に
4. ハードコードされた認証情報: `SENDGRID_API_KEY`、`SMS_API_KEY`
5. デストラクタでのリソース管理: `__del__` での `conn.close()` は信頼できない
6. セキュリティ問題: `password_hash` を `get_user()` の戻り値に含めている
7. バリデーション不足: `change_role()` でロールの入力チェックがない
8. 誤った設計: `user_id` を電話番号として使っている

**`legacy/report_generator.py`**
1. データ収集とフォーマット生成の混在 (SRP違反)
2. DRY違反: `gen_rep()` と `export_csv()` で同じクエリが重複
3. マジックナンバー: `10`(在庫警告閾値)
4. 略語の命名: `gen_rep`、`t`、`sd`、`ed`
5. 一貫しないエラーハンドリング: 文字列で返す場合と例外の場合が混在
6. デッドコード: `old_monthly_report()` が削除されずに残っている

---

## 自分の解答との比較ポイント

1. **責務の分割は一致しているか?** 同じ数のクラスでなくても良い
2. **テストが DB なしで書けるか?** これが最重要の評価基準
3. **新しいクーポンの追加で既存コードを変更しないか?** OCP の確認
4. **ADR に設計判断を記録したか?** なぜその構造を選んだかを説明できるか
