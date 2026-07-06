# テーマ C: 習慣トラッカー (Habit Tracker) 詳細仕様

## アプリ概要

毎日継続したい習慣を登録し、実施した日を記録することで、ストリーク(Streak / 連続記録日数)・完了率・カレンダービューで進捗を可視化する Web アプリです。「1 ヶ月で何日続いたか」をグラフで確認し、モチベーション維持をサポートします。

---

## ターゲットユーザー

- 「毎日英語学習」「週 3 回運動」のような習慣を継続したい人
- 自分の行動パターンをデータで振り返りたい人

---

## 機能要件

### MVP に含める機能(Must have)

#### 認証

- [ ] メールアドレス + パスワードでユーザー登録できる
- [ ] ログイン・ログアウトができる
- [ ] 認証なしでアクセスした場合、ログインページにリダイレクトされる

#### 習慣の管理

- [ ] 習慣を作成・編集・削除できる
  - 習慣には名前・説明・頻度(毎日 / 週次)・目標回数を設定できる
  - 受け入れ条件: 作成した習慣が一覧に表示される
- [ ] 習慣ごとに「今日実施した」をチェックできる
  - 受け入れ条件: チェックすると即座に反映され、当日の完了状態が保持される
  - 日付をまたいでも前日の記録は変わらない

#### 統計・可視化

- [ ] 習慣ごとのストリーク(連続実施日数)が表示される
  - 受け入れ条件: 昨日と今日に実施していれば連続とカウントされる
- [ ] 過去 30 日間のカレンダービューで実施状況が表示される
  - 受け入れ条件: 実施日は色付きセル、未実施日は白・グレーで表示される
- [ ] 今月の完了率(%)が表示される

---

### 将来の機能(Should have)

- 週次・月次のサマリーメール通知
- 習慣のカテゴリ分け
- 達成リマインダー通知(プッシュ通知)
- 習慣ごとのメモ(その日の気づきを記録)
- 複数ユーザーとの習慣シェア・比較

---

### スコープ外(Won't have)

- Apple Health / Google Fit 連携
- モバイルアプリ(PWA は将来対応候補)
- 習慣の実施時間の計測(Pomodoro タイマー等)

---

## データベーススキーマ

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100) NOT NULL,
    timezone        VARCHAR(50) NOT NULL DEFAULT 'Asia/Tokyo',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE habit_frequency AS ENUM ('daily', 'weekly');

CREATE TABLE habits (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    frequency       habit_frequency NOT NULL DEFAULT 'daily',
    target_per_week INTEGER,       -- weekly の場合: 週に何回が目標か
    color           VARCHAR(7),    -- HEX カラーコード (#3B82F6 等)
    is_archived     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE habit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    habit_id    UUID NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date    DATE NOT NULL,
    note        TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(habit_id, log_date)  -- 同一日に同じ習慣を二重記録しない
);

-- 検索・集計用インデックス
CREATE INDEX idx_habits_user_id ON habits(user_id);
CREATE INDEX idx_habit_logs_habit_id_date ON habit_logs(habit_id, log_date DESC);
CREATE INDEX idx_habit_logs_user_date ON habit_logs(user_id, log_date DESC);
```

### タイムゾーンの扱いについて

「今日実施したか」はユーザーのタイムゾーンに依存します。日本時間の深夜 0 時を「今日」の区切りとするため、`users.timezone` を持ちます。

```python
from datetime import date
from zoneinfo import ZoneInfo

def get_today_for_user(user_timezone: str) -> date:
    """ユーザーのタイムゾーンでの今日の日付を返す"""
    tz = ZoneInfo(user_timezone)
    from datetime import datetime
    return datetime.now(tz=tz).date()
```

---

## ストリーク計算アルゴリズム

```python
from datetime import date, timedelta
from typing import list

def calculate_streak(log_dates: list[date], today: date) -> int:
    """
    連続実施日数を計算する。
    今日または昨日が含まれていない場合は 0 を返す。
    """
    if not log_dates:
        return 0

    sorted_dates = sorted(set(log_dates), reverse=True)

    # 今日または昨日から始まっていない場合はストリーク 0
    yesterday = today - timedelta(days=1)
    if sorted_dates[0] < yesterday:
        return 0

    streak = 0
    expected = sorted_dates[0]  # 最新日から遡る

    for log_date in sorted_dates:
        if log_date == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        else:
            break

    return streak
```

---

## API 設計

### 認証

```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### 習慣

```
GET    /api/v1/habits                   習慣一覧(アーカイブ除く)
POST   /api/v1/habits                   習慣作成
GET    /api/v1/habits/{id}              習慣詳細
PUT    /api/v1/habits/{id}              習慣更新
DELETE /api/v1/habits/{id}              習慣削除(物理削除ではなくアーカイブ)
```

### 習慣ログ(記録)

```
GET    /api/v1/habits/{habit_id}/logs   ログ一覧(クエリパラメータ: from, to)
POST   /api/v1/habits/{habit_id}/logs   今日の記録を追加
DELETE /api/v1/habits/{habit_id}/logs/{log_date}  特定日の記録を削除
```

### 統計

```
GET    /api/v1/habits/{habit_id}/stats  統計情報(ストリーク・完了率・カレンダーデータ)
GET    /api/v1/stats/summary            全習慣のサマリー(今日の完了数・全体完了率)
```

### 統計 API のレスポンス例

```json
GET /api/v1/habits/550e8400-.../stats?from=2026-06-01&to=2026-06-30

{
  "habit_id": "550e8400-...",
  "name": "毎日英単語 10 個",
  "current_streak": 12,
  "longest_streak": 21,
  "completion_rate_this_month": 86.7,
  "total_logs": 26,
  "calendar": {
    "2026-06-01": true,
    "2026-06-02": true,
    "2026-06-03": false,
    ...
  }
}
```

---

## フロントエンド画面構成

```
/              ランディング(未ログイン時)
/login         ログイン
/register      ユーザー登録
/today         今日のチェックリスト(メイン画面)
/habits        習慣一覧・管理
/habits/:id    習慣詳細・統計・カレンダービュー
```

### コンポーネント構成

```
src/
├── components/
│   ├── habits/
│   │   ├── HabitCard.tsx          # 今日のチェックカード
│   │   ├── HabitForm.tsx          # 作成・編集フォーム
│   │   ├── HabitCalendar.tsx      # カレンダービュー
│   │   └── StreakBadge.tsx        # ストリーク表示
│   ├── stats/
│   │   ├── CompletionChart.tsx    # 棒グラフ・折れ線グラフ
│   │   └── MonthlyHeatmap.tsx     # 月次ヒートマップ
│   └── shared/
│       ├── ColorPicker.tsx
│       └── ProgressRing.tsx       # 円形プログレスバー
├── pages/
│   ├── TodayPage.tsx
│   ├── HabitsPage.tsx
│   └── HabitDetailPage.tsx
└── hooks/
    ├── useHabits.ts
    ├── useHabitLogs.ts
    └── useHabitStats.ts
```

---

## データ可視化ライブラリの選択

グラフ・カレンダーの実装には以下のライブラリを推奨します。

| ライブラリ | 用途 | 特徴 |
|-----------|------|------|
| Recharts | 棒グラフ・折れ線グラフ | React 向け。カスタマイズしやすい |
| react-calendar-heatmap | GitHub 草風のヒートマップ | SVG ベース。軽量 |
| date-fns | 日付操作 | 軽量・型安全 |

### Recharts での完了率グラフ実装例

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

type WeeklyData = {
  week: string  // "6/1 - 6/7"
  rate: number  // 0〜100
}

function CompletionChart({ data }: { data: WeeklyData[] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data}>
        <XAxis dataKey="week" />
        <YAxis domain={[0, 100]} unit="%" />
        <Tooltip formatter={(value) => `${value}%`} />
        <Bar dataKey="rate" fill="#3B82F6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

---

## 詰まりやすいポイントと対策

### 「今日」の定義がバグの温床になる

サーバーとクライアントで「今日」が異なることがあります(特にタイムゾーンが異なる場合)。

対策:
- ログの日付(`log_date`)はクライアント(ブラウザ)が持つユーザーのローカル日付を送る
- サーバー側では「今日」をバリデーションの判断基準にしない(翌日の記録も受け付ける等)

```typescript
// フロントエンドで今日の日付を ISO 8601 形式で送る
const today = new Date().toLocaleDateString('en-CA')  // "2026-07-05"

await api.post(`/habits/${habitId}/logs`, { log_date: today })
```

### ストリークのリアルタイム更新

習慣をチェックした瞬間にストリーク数が変わることを期待するユーザー体験のために:

```typescript
// Optimistic Update(楽観的更新): API の結果を待たずに UI を先に更新
const { mutate: checkHabit } = useMutation({
  mutationFn: (habitId: string) =>
    api.post(`/habits/${habitId}/logs`, { log_date: today }),
  onMutate: async (habitId) => {
    // キャッシュをすぐに更新(楽観的更新)
    await queryClient.cancelQueries({ queryKey: ["today-habits"] })
    const previous = queryClient.getQueryData(["today-habits"])
    queryClient.setQueryData(["today-habits"], (old: any) =>
      old.map((h: any) => h.id === habitId ? { ...h, completed_today: true } : h)
    )
    return { previous }
  },
  onError: (_err, _habitId, context) => {
    // 失敗したら元に戻す
    queryClient.setQueryData(["today-habits"], context?.previous)
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ["today-habits"] })
  },
})
```

### カレンダーUIの日付計算

`date-fns` ライブラリを使うと日付操作が大幅に簡単になります。

```typescript
import { eachDayOfInterval, startOfMonth, endOfMonth, format } from "date-fns"

// 今月のすべての日付を取得
const daysInMonth = eachDayOfInterval({
  start: startOfMonth(new Date()),
  end: endOfMonth(new Date()),
})

// カレンダーグリッドに変換
const calendarData = daysInMonth.map(day => ({
  date: format(day, "yyyy-MM-dd"),
  completed: logDates.includes(format(day, "yyyy-MM-dd")),
}))
```

---

このテーマの週次マイルストーンは `capstone/weekly-milestones.md` を参照してください。
