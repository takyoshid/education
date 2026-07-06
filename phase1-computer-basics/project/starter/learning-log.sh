#!/bin/bash
# learning-log.sh - 学習ログ管理ツール
#
# 使い方:
#   ./learning-log.sh add <内容> <学習時間(分)>
#   ./learning-log.sh list
#   ./learning-log.sh stats
#   ./learning-log.sh search <キーワード>
#   ./learning-log.sh delete <ID>
#   ./learning-log.sh today
#
# データ保存先: ~/.learning_log/records.csv
# フォーマット: ID,日付,内容,分数

# --- 設定 ---
# データ保存ディレクトリとファイルのパス
LOG_DIR="$HOME/.learning_log"
RECORDS_FILE="$LOG_DIR/records.csv"

# --- 初期化 ---
# データディレクトリが存在しなければ作成する
# (この部分はスターターコードが提供済み)
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

# --- add コマンド: 学習記録を追加する ---
# 引数:
#   $1 = 学習内容（文字列）
#   $2 = 学習時間（分・数値）
cmd_add() {
    # TODO: 引数チェックを実装する
    # ヒント: $# で引数の数を確認する。2つ未満ならエラー
    # ヒント: $2 が数値かどうかを grep -qE '^[0-9]+$' で確認する

    local CONTENT="$1"
    local MINUTES="$2"
    local TODAY
    TODAY=$(date +%Y-%m-%d)

    # TODO: 次の ID を計算する
    # ヒント: RECORDS_FILE が空でなければ最後の行の1列目+1、空なら1
    local NEXT_ID=1

    # TODO: CSV 行を作成して RECORDS_FILE に追記する
    # フォーマット: ID,日付,内容,分数
    # ヒント: echo "..." >> "$RECORDS_FILE"

    echo "記録を追加しました: [$TODAY] $CONTENT ($MINUTES 分)"
}

# --- list コマンド: 記録を一覧表示する ---
cmd_list() {
    # TODO: RECORDS_FILE が空かどうか確認する
    # ヒント: [ ! -s "$RECORDS_FILE" ] でファイルが空かどうか判定できる

    echo "=== 学習記録一覧 ==="

    # TODO: RECORDS_FILE の各行を読み込み、整形して表示する
    # ヒント: while IFS=',' read -r ID DATE CONTENT MINUTES; do ... done < "$RECORDS_FILE"
    # ヒント: printf でフォーマットを整える
    # 例: printf "%-4s %-12s %-45s %5s 分\n" "$ID" "$DATE" "$CONTENT" "$MINUTES"

    # TODO: 最後に合計学習時間を表示する
    # ヒント: awk -F',' '{sum += $4} END {print sum}' "$RECORDS_FILE"
    # ヒント: 分を時間・分に変換する（/ 60 と % 60 を使う）
}

# --- stats コマンド: 統計情報を表示する ---
cmd_stats() {
    # TODO: 記録が0件の場合は「記録がありません」を表示して終了する

    echo "=== 学習統計 ==="

    # TODO: 以下の統計を計算して表示する
    # 1. 総記録数 (wc -l を使う)
    # 2. 総学習時間 (awk で $4 列を合計)
    # 3. 平均学習時間 (総時間 / 総記録数)
    # 4. （追加）最長セッション
    # 5. （追加）直近7日間の学習時間
}

# --- search コマンド: キーワード検索 ---
cmd_search() {
    # TODO: 引数チェック（キーワードが必要）

    local KEYWORD="$1"

    echo "「$KEYWORD」の検索結果:"

    # TODO: RECORDS_FILE から KEYWORD を含む行を grep で検索して表示する
    # ヒント: grep -i "$KEYWORD" "$RECORDS_FILE" | while IFS=',' read ...
}

# --- delete コマンド: 記録を削除する ---
cmd_delete() {
    # TODO: 引数チェック（ID が必要）
    # TODO: 指定された ID の行が存在するか確認する

    local ID="$1"

    # TODO: 指定した ID の行を除いた内容で一時ファイルを作り、元ファイルを置き換える
    # ヒント: grep -v "^${ID}," "$RECORDS_FILE" > /tmp/learning_log_tmp.csv
    # ヒント: mv /tmp/learning_log_tmp.csv "$RECORDS_FILE"

    echo "ID $ID の記録を削除しました"
}

# --- today コマンド: 今日の記録を表示する ---
cmd_today() {
    local TODAY
    TODAY=$(date +%Y-%m-%d)

    echo "=== 今日の学習記録 ($TODAY) ==="

    # TODO: RECORDS_FILE から今日の日付の行を grep で抽出して表示する
    # TODO: 今日の合計学習時間も表示する
}

# --- メイン処理 ---
# 初期化を実行
init

# 引数がない場合はヘルプを表示
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# サブコマンドを振り分ける
COMMAND="$1"
shift  # $1 を消費して、$2 以降を $1 以降にシフトする

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
        echo "エラー: 不明なコマンド: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
