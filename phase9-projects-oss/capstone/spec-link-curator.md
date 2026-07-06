# テーマ B: リンクキュレーターアプリ (Link Curator) 詳細仕様

## アプリ概要

読んだ技術記事・Web ページの URL を保存し、タグとメモを付けて整理できる Web アプリです。PostgreSQL の全文検索(Full-Text Search)を使ってタイトル・メモ・タグを横断的に検索できます。URL を貼り付けると、ページタイトル・ファビコンを自動取得します。

---

## ターゲットユーザー

技術記事・論文・ブログを大量に読む学習者・研究者・エンジニアで、「あの記事どこだっけ?」という問題を解決したい人。

---

## 機能要件

### MVP に含める機能(Must have)

#### 認証

- [ ] メールアドレス + パスワードでユーザー登録できる
  - 受け入れ条件: 登録後、JWT アクセストークンが返り、ログイン状態になる
- [ ] ログイン・ログアウトができる
- [ ] 認証なしでアクセスした場合、ログインページにリダイレクトされる

#### リンク保存

- [ ] URL を入力するとリンクを保存できる
  - 受け入れ条件: URL が DB に保存され、リンク一覧に表示される
- [ ] URL 入力時にページタイトルが自動取得される
  - 受け入れ条件: バックグラウンドでタイトルが取得され、保存後または数秒後に表示される
  - 取得に失敗した場合は URL をタイトルとして表示
- [ ] リンクにメモ(自由記述)を付けられる
- [ ] リンクを削除できる

#### タグ管理

- [ ] リンクにタグを複数付けられる
  - 受け入れ条件: 既存タグを選択、または新しいタグを入力して付与できる
- [ ] タグで絞り込みできる
  - 受け入れ条件: タグをクリックすると、そのタグのついたリンクのみ表示される
- [ ] タグの一覧が表示される

#### 検索

- [ ] タイトル・メモ・タグを横断的に全文検索できる
  - 受け入れ条件: 検索ワードを入力すると、1 秒以内に結果が表示される
  - 部分一致で検索できる

---

### 将来の機能(Should have)

- ブラウザ拡張機能(ワンクリックで URL 保存)
- 公開/非公開の切り替え
- コレクション(複数タグをまとめるフォルダ)
- インポート(ブラウザのブックマーク HTML から)
- エクスポート(CSV, JSON)

---

### スコープ外(Won't have)

- 他ユーザーとのリンク共有・公開
- リンク先のコンテンツ全文の保存(ウェブアーカイブ機能)
- モバイルアプリ(レスポンシブ Web のみ)

---

## データベーススキーマ

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100) NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE links (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    url         TEXT NOT NULL,
    title       VARCHAR(500),
    favicon_url TEXT,
    memo        TEXT,
    -- 全文検索用インデックス列
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(memo, '')), 'B')
    ) STORED,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tags (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name    VARCHAR(100) NOT NULL,
    UNIQUE(user_id, name)
);

CREATE TABLE link_tags (
    link_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    tag_id  UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (link_id, tag_id)
);

-- 全文検索インデックス
CREATE INDEX idx_links_search_vector ON links USING GIN(search_vector);
CREATE INDEX idx_links_user_id ON links(user_id);
CREATE INDEX idx_tags_user_id ON tags(user_id);
```

### なぜ GENERATED ALWAYS AS STORED カラムを使うか

`TSVECTOR` カラムを計算列として定義することで、INSERT / UPDATE 時に自動更新されます。アプリケーション側で `tsvector` を計算する処理を書く必要がなくなります。

---

## 全文検索の実装

### PostgreSQL の全文検索クエリ例

```sql
-- "react hooks" で検索(title と memo を横断)
SELECT l.*, ts_rank(l.search_vector, query) AS rank
FROM links l, to_tsquery('english', 'react & hooks') query
WHERE l.user_id = $1
  AND l.search_vector @@ query
ORDER BY rank DESC;
```

### タグを含む検索の実装

```sql
-- タグ名も含めて検索する場合(タグは JOIN で取得)
SELECT DISTINCT l.*
FROM links l
LEFT JOIN link_tags lt ON lt.link_id = l.id
LEFT JOIN tags t ON t.id = lt.tag_id
WHERE l.user_id = $1
  AND (
    l.search_vector @@ to_tsquery('english', $2)
    OR t.name ILIKE '%' || $2 || '%'
  );
```

---

## API 設計

### 認証

```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### リンク

```
GET    /api/v1/links             リンク一覧(クエリパラメータ: tag, search, page, per_page)
POST   /api/v1/links             リンク作成
GET    /api/v1/links/{id}        リンク詳細
PUT    /api/v1/links/{id}        リンク更新(メモ・タグ)
DELETE /api/v1/links/{id}        リンク削除
```

### タグ

```
GET    /api/v1/tags              タグ一覧(使用数付き)
DELETE /api/v1/tags/{id}         タグ削除(使用中のリンクから外れる)
```

### リクエスト/レスポンス例

**POST /api/v1/links のリクエスト:**

```json
{
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "memo": "公式チュートリアル。依存性注入のセクションが参考になった",
  "tags": ["fastapi", "python", "tutorial"]
}
```

**レスポンス (201 Created):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "title": "FastAPI - Tutorial - User Guide",
  "favicon_url": "https://fastapi.tiangolo.com/img/favicon.png",
  "memo": "公式チュートリアル。依存性注入のセクションが参考になった",
  "tags": ["fastapi", "python", "tutorial"],
  "created_at": "2026-07-05T10:00:00Z"
}
```

---

## URL からタイトルを自動取得する実装

### バックグラウンドタスクとして実装する

FastAPI の `BackgroundTasks` を使い、レスポンスを返した後にタイトルを取得します。

```python
from fastapi import BackgroundTasks
import httpx
from bs4 import BeautifulSoup

async def fetch_page_title(link_id: str, url: str, db: AsyncSession):
    """バックグラウンドでページタイトルを取得して DB を更新する"""
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "LinkCurator/1.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        if title:
            # DB 更新
            await update_link_title(db, link_id, title.get_text(strip=True))
    except Exception:
        # タイトル取得失敗は致命的ではない。ログだけ記録
        pass

@router.post("/links", status_code=201)
async def create_link(
    data: LinkCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = await link_service.create(db, data, current_user.id)
    # タイトル取得をバックグラウンドで実行
    background_tasks.add_task(fetch_page_title, str(link.id), data.url, db)
    return link
```

---

## フロントエンド画面構成

```
/              ランディング(未ログイン時)
/login         ログイン
/register      ユーザー登録
/links         リンク一覧(メイン画面)
/links/:id     リンク詳細・編集
```

### コンポーネント構成

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── links/
│   │   ├── LinkCard.tsx
│   │   ├── LinkForm.tsx
│   │   └── LinkList.tsx
│   ├── tags/
│   │   ├── TagBadge.tsx
│   │   ├── TagFilter.tsx
│   │   └── TagInput.tsx    # タグ入力(オートコンプリート付き)
│   └── shared/
│       ├── SearchBar.tsx
│       └── Pagination.tsx
├── pages/
│   ├── LinksPage.tsx
│   ├── Login.tsx
│   └── Register.tsx
└── hooks/
    ├── useLinks.ts
    ├── useTags.ts
    └── useSearch.ts
```

---

## 詰まりやすいポイントと対策

### タイトル取得で CORS / SSL エラーが出る

バックエンドから `httpx` で外部 URL を取得するとき、SSL 証明書エラーや古いサイトでのタイムアウトが起きます。

対策:
- タイムアウトを `5.0` 秒に設定する
- `follow_redirects=True` を設定する
- 失敗したら静かに無視する(ユーザー体験に影響させない)

### `BeautifulSoup` の文字コード問題

一部のサイトは UTF-8 以外のエンコードを使います。

```python
# requests / httpx はエンコードを自動検出する
# BeautifulSoup の from_encoding を使う
soup = BeautifulSoup(response.content, "html.parser", from_encoding=response.encoding)
```

### PostgreSQL 全文検索の日本語対応

`to_tsvector('english', ...)` は英語の形態素解析を使います。日本語に対応するには `pg_bigm` 拡張が必要ですが、Render の無料プランでは使えない場合があります。

代替案:
1. **タイトル・メモに `ILIKE`** を使う(全文検索の代替として十分な場合が多い)
2. **`pg_trgm`** 拡張を使う(PostgreSQL 標準で利用可能、日本語のトライグラム検索)

```sql
-- pg_trgm を使った検索
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_links_title_trgm ON links USING GIN(title gin_trgm_ops);
CREATE INDEX idx_links_memo_trgm  ON links USING GIN(memo gin_trgm_ops);

-- 検索クエリ
SELECT * FROM links
WHERE user_id = $1
  AND (title ILIKE '%' || $2 || '%' OR memo ILIKE '%' || $2 || '%');
```

### タグのオートコンプリート

フロントエンドで「タグを入力すると既存のタグを候補表示する」実装です。

```typescript
// debounce を使って API 呼び出しを間引く
const [tagQuery, setTagQuery] = useState("")
const debouncedQuery = useDebounce(tagQuery, 300) // 300ms 待つ

const { data: suggestions } = useQuery({
  queryKey: ["tags", "suggest", debouncedQuery],
  queryFn: () => api.get(`/tags?q=${debouncedQuery}`),
  enabled: debouncedQuery.length > 0,
})
```

---

このテーマの週次マイルストーンは `capstone/weekly-milestones.md` を参照してください。
