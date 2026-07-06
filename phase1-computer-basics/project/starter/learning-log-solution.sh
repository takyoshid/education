#!/bin/bash
# learning-log.sh - 学習ログ管理ツール（解答例）
#
# 注意: これは解答例です。スターターコード (learning-log.sh) を先に自分で実装してから見てください。

set -u

# --- 設定 ---
LOG_DIR="$HOME/.learning_log"
RECORDS_FILE="$LOG_DIR/records.csv"

# --- 初期化 ---
init() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
    fi
    if [ ! -f "$RECORDS_FILE" ]; then
        touch "$RECORDS_FILE"
    fi
}

# --- ヘルプ表示 ---
show_help() {
    echo "学習ログ管理ツール"
    echo ""
    echo "使い方:"
    echo "  $0 add <内容> <学習時間(分)>    学習記録を追加"
    echo "  $0 list                          記録を一覧表示"
    echo "  $0 stats                         統計情報を表示"
    echo "  $0 search <キーワード>           キーワードで検索"
    echo "  $0 delete <ID>                   指定IDの記録を削除"
    echo "  $0 today                         今日の記録を表示"
}

# --- 共通ユーティリティ ---

# 分を "X 時間 Y 分" の形式に変換する
format_minutes() {
    local TOTAL=$1
    local HOURS=$((TOTAL / 60))
    local MINS=$((TOTAL % 60))
    if [ "$HOURS" -gt 0 ]; then
        echo "${HOURS} 時間 ${MINS} 分"
    else
        echo "${MINS} 分"
    fi
}

# ファイルが空かチェック
is_empty() {
    [ ! -s "$RECORDS_FILE" ]
}

# --- add コマンド ---
cmd_add() {
    # 引数チェック
    if [ $# -lt 2 ]; then
        echo "エラー: 引数が不足しています" >&2
        echo "使い方: $0 add <内容> <学習時間(分)>" >&2
        exit 1
    fi

    local CONTENT="$1"
    local MINUTES="$2"
    local TODAY
    TODAY=$(date +%Y-%m-%d)

    # 学習時間が数値かチェック
    if ! echo "$MINUTES" | grep -qE '^[0-9]+$'; then
        echo "エラー: 学習時間は正の整数で入力してください (例: 60)" >&2
        exit 1
    fi

    # 0分のチェック
    if [ "$MINUTES" -eq 0 ]; then
        echo "エラー: 学習時間は1分以上を入力してください" >&2
        exit 1
    fi

    # 次の ID を計算
    local NEXT_ID
    if is_empty; then
        NEXT_ID=1
    else
        NEXT_ID=$(tail -1 "$RECORDS_FILE" | cut -d',' -f1)
        NEXT_ID=$((NEXT_ID + 1))
    fi

    # CSV に追記
    echo "${NEXT_ID},${TODAY},${CONTENT},${MINUTES}" >> "$RECORDS_FILE"

    echo "記録を追加しました (ID: $NEXT_ID)"
    echo "  日付: $TODAY"
    echo "  内容: $CONTENT"
    echo "  時間: $MINUTES 分"
}

# --- list コマンド ---
cmd_list() {
    if is_empty; then
        echo "記録がありません。'$0 add' で記録を追加してください。"
        return 0
    fi

    echo "=== 学習記録一覧 ==="
    printf "%-4s  %-12s  %-45s  %6s\n" "ID" "日付" "内容" "分数"
    printf "%-4s  %-12s  %-45s  %6s\n" "----" "------------" "---------------------------------------------" "------"

    while IFS=',' read -r ID DATE CONTENT MINUTES; do
        printf "%-4s  %-12s  %-45s  %5s 分\n" "$ID" "$DATE" "$CONTENT" "$MINUTES"
    done < "$RECORDS_FILE"

    # 合計学習時間
    local TOTAL
    TOTAL=$(awk -F',' '{sum += $4} END {print sum+0}' "$RECORDS_FILE")
    local COUNT
    COUNT=$(wc -l < "$RECORDS_FILE" | tr -d ' ')

    echo ""
    echo "合計: $COUNT 件 / $(format_minutes "$TOTAL")"
}

# --- stats コマンド ---
cmd_stats() {
    if is_empty; then
        echo "記録がありません。"
        return 0
    fi

    local COUNT
    COUNT=$(wc -l < "$RECORDS_FILE" | tr -d ' ')

    local TOTAL
    TOTAL=$(awk -F',' '{sum += $4} END {print sum+0}' "$RECORDS_FILE")

    local AVG
    AVG=$((TOTAL / COUNT))

    # 最長セッション
    local MAX_LINE
    MAX_LINE=$(sort -t',' -k4 -rn "$RECORDS_FILE" | head -1)
    local MAX_MINUTES
    MAX_MINUTES=$(echo "$MAX_LINE" | cut -d',' -f4)
    local MAX_CONTENT
    MAX_CONTENT=$(echo "$MAX_LINE" | cut -d',' -f3)

    # 最短セッション
    local MIN_LINE
    MIN_LINE=$(sort -t',' -k4 -n "$RECORDS_FILE" | head -1)
    local MIN_MINUTES
    MIN_MINUTES=$(echo "$MIN_LINE" | cut -d',' -f4)
    local MIN_CONTENT
    MIN_CONTENT=$(echo "$MIN_LINE" | cut -d',' -f3)

    # 直近7日間
    local WEEK_AGO
    # date コマンドの書き方が macOS と Linux で異なる
    if date -v-7d +%Y-%m-%d > /dev/null 2>&1; then
        # macOS
        WEEK_AGO=$(date -v-7d +%Y-%m-%d)
    else
        # Linux
        WEEK_AGO=$(date -d "7 days ago" +%Y-%m-%d)
    fi

    local WEEK_TOTAL
    WEEK_TOTAL=$(awk -F',' -v cutoff="$WEEK_AGO" '$2 >= cutoff {sum += $4} END {print sum+0}' "$RECORDS_FILE")

    echo "=== 学習統計 ==="
    echo "総記録数: $COUNT 件"
    echo "総学習時間: $(format_minutes "$TOTAL")"
    echo "平均学習時間: $AVG 分/セッション"
    echo "最長セッション: $MAX_MINUTES 分 - \"$MAX_CONTENT\""
    echo "最短セッション: $MIN_MINUTES 分 - \"$MIN_CONTENT\""
    echo "直近7日間: $(format_minutes "$WEEK_TOTAL")"
}

# --- search コマンド ---
cmd_search() {
    if [ $# -eq 0 ]; then
        echo "エラー: 検索キーワードを指定してください" >&2
        echo "使い方: $0 search <キーワード>" >&2
        exit 1
    fi

    local KEYWORD="$1"

    echo "「$KEYWORD」の検索結果:"

    local FOUND=0
    while IFS=',' read -r ID DATE CONTENT MINUTES; do
        # 内容にキーワードが含まれるか確認（大文字小文字無視）
        if echo "$CONTENT" | grep -qi "$KEYWORD"; then
            printf "  [%s] %s - %s (%s 分)\n" "$ID" "$DATE" "$CONTENT" "$MINUTES"
            FOUND=$((FOUND + 1))
        fi
    done < "$RECORDS_FILE"

    if [ "$FOUND" -eq 0 ]; then
        echo "  該当する記録が見つかりませんでした。"
    else
        echo ""
        echo "$FOUND 件見つかりました。"
    fi
}

# --- delete コマンド ---
cmd_delete() {
    if [ $# -eq 0 ]; then
        echo "エラー: 削除する ID を指定してください" >&2
        echo "使い方: $0 delete <ID>" >&2
        exit 1
    fi

    local ID="$1"

    # ID が数値かチェック
    if ! echo "$ID" | grep -qE '^[0-9]+$'; then
        echo "エラー: ID は数値で指定してください" >&2
        exit 1
    fi

    # 指定 ID の行が存在するか確認
    if ! grep -q "^${ID}," "$RECORDS_FILE"; then
        echo "エラー: ID $ID の記録が見つかりません" >&2
        exit 1
    fi

    # 対象行の内容を表示
    local TARGET_LINE
    TARGET_LINE=$(grep "^${ID}," "$RECORDS_FILE")
    local CONTENT
    CONTENT=$(echo "$TARGET_LINE" | cut -d',' -f3)
    local DATE
    DATE=$(echo "$TARGET_LINE" | cut -d',' -f2)

    # 確認プロンプト
    echo "削除する記録: [$DATE] $CONTENT"
    printf "本当に削除しますか？ (y/N): "
    read -r CONFIRM

    if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
        echo "削除をキャンセルしました。"
        return 0
    fi

    # 指定 ID 以外の行を一時ファイルに書き出し、元ファイルを置き換える
    local TMP_FILE
    TMP_FILE=$(mktemp)
    grep -v "^${ID}," "$RECORDS_FILE" > "$TMP_FILE"
    mv "$TMP_FILE" "$RECORDS_FILE"

    echo "ID $ID の記録を削除しました。"
}

# --- today コマンド ---
cmd_today() {
    local TODAY
    TODAY=$(date +%Y-%m-%d)

    echo "=== 今日の学習記録 ($TODAY) ==="

    local COUNT=0
    while IFS=',' read -r ID DATE CONTENT MINUTES; do
        if [ "$DATE" = "$TODAY" ]; then
            printf "  [%s] %s (%s 分)\n" "$ID" "$CONTENT" "$MINUTES"
            COUNT=$((COUNT + 1))
        fi
    done < "$RECORDS_FILE"

    if [ "$COUNT" -eq 0 ]; then
        echo "  今日の記録はありません。"
        return 0
    fi

    # 今日の合計時間
    local TODAY_TOTAL
    TODAY_TOTAL=$(awk -F',' -v today="$TODAY" '$2 == today {sum += $4} END {print sum+0}' "$RECORDS_FILE")

    echo ""
    echo "今日の合計: $COUNT セッション / $(format_minutes "$TODAY_TOTAL")"
}

# --- メイン処理 ---
init

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    add)
        cmd_add "$@"
        ;;
    list)
        cmd_list
        ;;
    stats)
        cmd_stats
        ;;
    search)
        cmd_search "$@"
        ;;
    delete)
        cmd_delete "$@"
        ;;
    today)
        cmd_today
        ;;
    help | --help | -h)
        show_help
        ;;
    *)
        echo "エラー: 不明なコマンド: $COMMAND" >&2
        echo ""
        show_help
        exit 1
        ;;
esac
