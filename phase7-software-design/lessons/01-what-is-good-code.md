# Lesson 01: 良いコードとは何か

## このレッスンで学ぶこと

- 「動くコード」と「良いコード」の違い
- コードの可読性(readability)とは何か
- 変更容易性(changeability / maintainability)とは何か
- 命名(naming)の技術と具体的な判断基準

---

## 1. なぜ「良いコード」を学ぶのか

プログラムは書いたその瞬間よりも、書いた後の時間の方がはるかに長いです。
ある調査では、エンジニアがコードを「読む時間」と「書く時間」の比率は **10:1** とも言われています。

つまり、コードは「実行されるもの」である前に「読まれるもの」です。

良いコードを書く理由は3つあります。

1. **自分自身のため**: 3ヶ月後の自分は、そのコードを書いたことすら忘れています
2. **チームのため**: チームメンバーが理解・修正できるコードが価値を持ちます
3. **ビジネスのため**: 変更しやすいコードは、ビジネスの変化に対応できます

---

## 2. 可読性(Readability)

可読性とは「コードを読んで、素早く正確に意図を理解できる度合い」です。

### 悪い例

```python
def calc(a, b, c):
    x = a * b
    y = x - (x * c / 100)
    return y
```

何が問題か:
- `calc` は何を計算するのか分からない
- `a`, `b`, `c` が何を表すのか分からない
- `x`, `y` も意味不明
- この関数を使う人は実装を読むしかない

### 改善例

```python
def calculate_discounted_price(unit_price: float, quantity: int, discount_percent: float) -> float:
    """割引後の合計価格を計算する。"""
    subtotal = unit_price * quantity
    discount_amount = subtotal * discount_percent / 100
    return subtotal - discount_amount
```

改善点:
- 関数名が「何をするか」を説明している
- 引数名が「何を表すか」を説明している
- 中間変数にも意味のある名前がついている
- 型ヒント(type hint)で引数の型が明確

---

## 3. 変更容易性(Changeability)

変更容易性とは「新しい要件が来たとき、最小限の変更で対応できる度合い」です。

### 悪い例

```python
def send_notification(user_id: int, message: str, method: str) -> None:
    if method == "email":
        # メール送信の詳細実装
        import smtplib
        server = smtplib.SMTP("smtp.example.com", 587)
        server.starttls()
        server.login("user@example.com", "password123")
        server.sendmail("user@example.com", f"{user_id}@example.com", message)
        server.quit()
    elif method == "sms":
        # SMS送信の詳細実装
        import requests
        requests.post("https://sms-api.example.com/send", json={
            "to": f"+81{user_id}",
            "body": message,
            "api_key": "hardcoded_key_123"
        })
    elif method == "push":
        # プッシュ通知の詳細実装
        import requests
        requests.post("https://push-api.example.com/notify", json={
            "device_token": user_id,
            "message": message
        })
    # 新しい通知方法が増えるたびにここに追加していく...
```

何が問題か:
- 通知方法が増えるたびにこの関数を修正しなければならない
- 一つの変更が他の通知方法に影響を与えるリスクがある
- テストが書きにくい(実際のメール/SMSサーバーが必要になる)
- 認証情報がハードコード(hardcode)されている

改善の方向性(Lesson 03, 04で詳しく扱います):
- 通知方法ごとにクラスを分離する
- 共通のインターフェースを定義する
- 新しい通知方法は既存コードを変更せず追加できるようにする

---

## 4. 命名の技術

命名はプログラミングで最も重要なスキルの一つです。
良い名前は、コメントなしで意図を伝えます。

### 原則1: 意図を明確にする

**悪い例** → **良い例** の対比:

```python
# 悪い: 何のリストか不明
d = []

# 良い: 何のリストかが明確
expired_user_ids = []
```

```python
# 悪い: フラグの意味が不明
if flag:
    ...

# 良い: フラグの意味が明確
if is_email_verified:
    ...
```

```python
# 悪い: 何をチェックするのか不明
def check(u):
    ...

# 良い: 何をチェックするかが明確
def is_account_active(user: User) -> bool:
    ...
```

### 原則2: 嘘をつかない

名前と実装が食い違うのは最悪のパターンです。

```python
# 悪い: get は副作用を持つべきでない慣習なのに、DBに書き込んでいる
def get_user(user_id: int) -> User:
    user = db.find(user_id)
    db.update_last_access(user_id)  # 副作用がある!
    return user

# 良い: 副作用があることが名前から分かる
def get_user_and_record_access(user_id: int) -> User:
    user = db.find(user_id)
    db.update_last_access(user_id)
    return user

# さらに良い: 責務を分離する
def get_user(user_id: int) -> User:
    return db.find(user_id)

def record_user_access(user_id: int) -> None:
    db.update_last_access(user_id)
```

### 原則3: 発音できる名前を使う

チームでの会話やコードレビューで話しやすい名前を使います。

```python
# 悪い: 発音できない略語
usrMgrObj = UserManager()
genYyyyMmDd = generate_date_string()

# 良い: 発音できる
user_manager = UserManager()
formatted_date = generate_date_string()
```

### 原則4: 検索しやすい名前を使う

マジックナンバー(magic number)には名前をつけます。

```python
# 悪い: 86400 が何を意味するか不明
if elapsed_seconds > 86400:
    expire_session()

# 良い: 意味が明確
SECONDS_PER_DAY = 86_400  # Pythonでは _ で桁区切り可能

if elapsed_seconds > SECONDS_PER_DAY:
    expire_session()
```

### 原則5: コンテキストを活用する

クラスのメソッドやモジュールの関数は、コンテキストが名前の一部になります。

```python
# 悪い: クラス名を繰り返している
class User:
    def get_user_name(self) -> str:  # "user" が重複
        return self.name

    def set_user_email(self, email: str) -> None:  # "user" が重複
        self.email = email

# 良い: コンテキスト (User) は既に分かっている
class User:
    def get_name(self) -> str:
        return self.name

    def set_email(self, email: str) -> None:
        self.email = email
```

### 命名の品詞ルール

| 対象 | 使う品詞 | 例 |
|------|---------|-----|
| 変数・属性 | 名詞 | `user_name`, `order_count` |
| 真偽値 | `is_`, `has_`, `can_`, `should_` + 形容詞/過去分詞 | `is_active`, `has_permission` |
| 関数・メソッド | 動詞 + 名詞 | `calculate_tax()`, `send_email()` |
| クラス | 名詞 (単数形) | `UserRepository`, `OrderService` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |

---

## 5. コメントの正しい使い方

良いコードにもコメントは必要ですが、使い方を間違えると害になります。

### コメントで補うのではなく、コードを改善する

```python
# 悪い: コードが不明瞭なのをコメントで補っている
# ユーザーの年齢が18以上かつアクティブであるか確認する
if u.age >= 18 and u.status == 1:
    ...

# 良い: コードが自己説明的
def is_eligible_for_adult_content(user: User) -> bool:
    return user.age >= ADULT_AGE_THRESHOLD and user.is_active

if is_eligible_for_adult_content(user):
    ...
```

### コメントが必要な場面

「なぜ(why)」を説明するコメントは価値があります。
「何を(what)」するかはコードから読めるはずです。

```python
# 悪い: コードを言い換えているだけ (冗長なコメント)
# iを1増やす
i += 1

# 良い: なぜその処理をするのかを説明している
# Pythonの int は任意精度だが、外部APIが32bit整数を期待するため
# オーバーフローを防ぐためにマスクする
value = raw_value & 0xFFFFFFFF
```

```python
# 良い: 直感に反する実装の理由を説明している
# time.sleep(0) はCPUをリリースして他のスレッドに実行機会を与える
# 高頻度ループ内でのスターベーション防止のために必要
time.sleep(0)
```

---

## 💡 コラム: 割れ窓と技術的負債

犯罪学に「割れ窓理論」という仮説があります。建物の割れた窓ガラスを放置すると、「ここは誰も気にかけていない」というメッセージになり、さらなる破壊や犯罪を呼び込む — 『達人プログラマー』はこれをソフトウェアに適用しました。**雑なコードが1つ放置されると、「この程度でいいんだ」という空気が生まれ、次の雑なコードの心理的ハードルが下がる。** 綺麗なコードベースで雑なコードは書きにくく、汚いコードベースで丁寧なコードを書く気は起きません。

もう一つ、現場の共通語になっている比喩が「**技術的負債**」です。急いで雑に書くことは借金に似ています。借りる(リリースを早める)こと自体は経営判断としてアリですが、**利息(変更のたびの余計な時間)は複利で増え**、返済(リファクタリング)を先送りするほど元本が膨らみ、最悪「利息の支払いで新機能開発が止まる」倒産状態に至ります。

「良いコード」とは、潔癖症の美学ではありません。**窓を直し、借金を管理する — チームの開発速度を将来にわたって守る経済活動**なのです。

---

## 6. まとめ

| 概念 | 一言で言うと |
|------|-------------|
| 可読性 | 読んで素早く理解できるか |
| 変更容易性 | 新要件に最小限の変更で対応できるか |
| 良い命名 | 意図を明確に、嘘をつかず、発音できる名前 |
| コメント | 「なぜ」を説明する。「何を」はコードで表現する |

**最も重要な原則**: コードは人間が読むために書く。コンピュータへの命令は二次的な目的です。

---

## 確認問題

**問題1**: 以下のコードの問題点を3つ以上挙げ、改善してください。

```python
def proc(l, x):
    r = []
    for i in l:
        if i > x:
            r.append(i)
    return r
```

**問題2**: 以下のコメントは「良いコメント」か「悪いコメント」か、理由とともに答えてください。

```python
# リストをソートする
items.sort()
```

```python
# sort() は安定ソートであることが保証されているため、
# 同じ優先度のタスクは挿入順が維持される
tasks.sort(key=lambda t: t.priority)
```

**問題3**: 変数名 `data` の問題点を説明してください。どのような名前が良いか、具体例を2つ挙げてください。

---

次のレッスン: [Lesson 02: 関数・クラス設計の原則](./02-function-class-design.md)
