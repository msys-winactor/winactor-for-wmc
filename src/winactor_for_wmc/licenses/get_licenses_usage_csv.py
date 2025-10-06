import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta

from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_path = kwargs.get("file_path")
    encoding = kwargs.get("encoding", "UTF-8")
    created_at_type = kwargs.get("created_at_type", "range")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")
    start_time = kwargs.get("start_time")
    end_time = kwargs.get("end_time")

    if not base_url or not token or not file_path:
        raise ValueError("WMC URL, アクセストークン, CSVファイル名 は必須項目です。")

    # createdAtTypeの検証と正規化
    if not created_at_type or created_at_type.strip() == "":
        created_at_type = "range"

    created_at_type = created_at_type.strip().lower()

    if created_at_type not in ["range", "before", "after"]:
        created_at_type = "range"

    # 検索パラメータの基本設定
    params = {
        "messageType": "partial",
        "message": "払い出し数",
        "sort": "createdAt",
        "sortDirection": "asc",
        "page": 1,
        "size": 100,
    }

    # createdAtTypeに応じた日付・時刻の処理とパラメータ設定
    if created_at_type == "range":
        # range: 両方の日付が入力されている場合のみ期間指定
        has_start = start_date and start_date.strip() != ""
        has_end = end_date and end_date.strip() != ""

        if has_start and has_end:
            # 両方入力されている場合：範囲指定
            params["createdAtType"] = "range"

            # 時刻の処理（未設定時のデフォルト値）
            if not start_time or start_time.strip() == "":
                start_time = "00:00:00"
            else:
                start_time = validate_time_format(start_time)

            if not end_time or end_time.strip() == "":
                end_time = "23:59:59"
            else:
                end_time = validate_time_format(end_time)

            # パラメータに追加
            params["createdAtDate1"] = start_date
            params["createdAtTime1"] = start_time
            params["createdAtDate2"] = end_date
            params["createdAtTime2"] = end_time

        elif has_start and not has_end:
            # 検索日1のみ入力：after扱い
            params["createdAtType"] = "after"

            if not start_time or start_time.strip() == "":
                start_time = "00:00:00"
            else:
                start_time = validate_time_format(start_time)

            params["createdAtDate1"] = start_date
            params["createdAtTime1"] = start_time

        elif not has_start and has_end:
            # 検索日2のみ入力：before扱い
            params["createdAtType"] = "before"

            if not end_time or end_time.strip() == "":
                end_time = "23:59:59"
            else:
                end_time = validate_time_format(end_time)

            params["createdAtDate1"] = end_date
            params["createdAtTime1"] = end_time

        else:
            # 両方未入力：期間指定なし（createdAtTypeを設定しない）
            # paramsにcreatedAtTypeを追加しない = 全期間検索
            pass

    elif created_at_type == "before":
        # before: 検索日1を使用（createdAtDate1 + createdAtTime1）
        if not start_date or start_date.strip() == "":
            raise ValueError("登録日時条件が「以前」の場合、検索日1は必須です。")

        params["createdAtType"] = "before"

        # 時刻の処理（未設定時は23:59:59）
        if not start_time or start_time.strip() == "":
            start_time = "23:59:59"
        else:
            start_time = validate_time_format(start_time)

        # パラメータに追加
        params["createdAtDate1"] = start_date
        params["createdAtTime1"] = start_time

    elif created_at_type == "after":  # pragma: no branch
        # after: 検索日1を使用（createdAtDate1 + createdAtTime1）
        if not start_date or start_date.strip() == "":  # pragma: no branch
            raise ValueError("登録日時条件が「以後」の場合、検索日1は必須です。")

        params["createdAtType"] = "after"

        # 時刻の処理（未設定時は00:00:00）
        if not start_time or start_time.strip() == "":
            start_time = "00:00:00"
        else:
            start_time = validate_time_format(start_time)

        # パラメータに追加
        params["createdAtDate1"] = start_date
        params["createdAtTime1"] = start_time

    # エンコーディングの変換
    if encoding == "MS932":
        file_encoding = "shift_jis"
    elif encoding == "UTF-8":
        file_encoding = "utf-8-sig"  # BOM付きUTF-8でExcel対応
    else:
        file_encoding = "utf-8-sig"

    client = WMCApiClient(base_url, token)

    # イベント一覧を取得（ページングを考慮して全件取得）
    all_events = []
    page = 1
    page_size = 100

    while True:
        params["page"] = page
        events_response = client.get("/events", params=params)
        events = events_response.get("items", [])

        if not events:
            break

        all_events.extend(events)

        # 最後のページかチェック
        if len(events) < page_size:
            break

        page += 1

    # ユーザー別のライセンス使用状況を整理
    user_license_data = defaultdict(list)

    for event in all_events:
        message = event.get("message", "")
        created_time = event.get("createdTime", 0)

        # ユーザ名を抽出
        user_match = re.search(r"ユーザ名=([^,]+)", message)
        if not user_match:
            continue

        user_name = user_match.group(1)

        # 日時をフォーマット
        formatted_time = unix_time_to_datetime(created_time)

        # イベントタイプを判定
        if "フローティングライセンスを払い出しました。" in message:
            event_type = "checkout"
        elif "フローティングライセンスを回収しました。" in message:
            event_type = "checkin"
        else:
            continue

        user_license_data[user_name].append(
            {"type": event_type, "time": formatted_time, "timestamp": created_time}
        )

    # CSVデータを作成
    csv_data = []
    csv_data.append(["WinActorユーザ名", "払い出し日時", "回収日時", "差分"])

    # ソート用のデータリスト
    sort_data = []

    for user_name, events in user_license_data.items():
        # イベントを時系列順にソート
        events.sort(key=lambda x: x["timestamp"])

        # 払い出しと回収をペアにする
        checkout_stack = []

        for event in events:
            if event["type"] == "checkout":  # pragma: no branch
                checkout_stack.append(event)
            elif event["type"] == "checkin":  # pragma: no branch
                if checkout_stack:
                    # 最新の払い出しと対応させる
                    checkout_event = checkout_stack.pop()

                    # 時間差を計算
                    checkout_time = datetime.strptime(
                        checkout_event["time"], "%Y/%m/%d %H:%M:%S"
                    )
                    checkin_time = datetime.strptime(event["time"], "%Y/%m/%d %H:%M:%S")
                    time_diff = checkin_time - checkout_time

                    # 時間差を文字列形式に変換（HH:MM:SS形式）
                    diff_str = format_time_difference(time_diff)

                    # ソート用データに追加
                    sort_data.append(
                        {
                            "user_name": user_name,
                            "checkout_time": checkout_event["time"],
                            "checkin_time": event["time"],
                            "diff": diff_str,
                            "checkin_timestamp": event["timestamp"],  # ソート用
                        }
                    )
                else:
                    # 対応する払い出しがない回収の場合
                    # 払い出し日時と差分を空欄にして出力
                    sort_data.append(
                        {
                            "user_name": user_name,
                            "checkout_time": "",  # 払い出し日時を空欄
                            "checkin_time": event["time"],
                            "diff": "",  # 差分を空欄
                            "checkin_timestamp": event["timestamp"],  # ソート用
                        }
                    )

        # 未回収の払い出しがある場合
        for remaining_checkout in checkout_stack:
            # ソート用データに追加（未回収は最優先）
            sort_data.append(
                {
                    "user_name": user_name,
                    "checkout_time": remaining_checkout["time"],
                    "checkin_time": "",  # 回収日時を空欄
                    "diff": "",  # 差分を空欄
                    "checkin_timestamp": 0,  # 未回収は0で最優先
                }
            )

    # ソート実行
    # 1. 回収日時が空欄（未回収）のものを最優先（checkin_timestamp = 0）
    # 2. その後は回収日時が新しい順（降順）
    sort_data.sort(key=lambda x: (x["checkin_timestamp"] != 0, -x["checkin_timestamp"]))

    # ソート済みデータをCSVデータに変換
    for item in sort_data:
        csv_data.append(
            [
                item["user_name"],
                item["checkout_time"],
                item["checkin_time"],
                item["diff"],
            ]
        )

    # CSVファイルに書き込み
    with open(file_path, "w", newline="", encoding=file_encoding) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    return


def validate_time_format(time_str):  # pragma: no cover
    """時刻フォーマットを検証し、正しい形式に変換"""
    # 既に正しい形式の場合はそのまま返す
    if re.match(r"^\d{2}:\d{2}:\d{2}$", time_str):  # pragma: no cover
        return time_str  # pragma: no cover

    # HH:MM形式の場合は秒を追加
    if re.match(r"^\d{1,2}:\d{2}$", time_str):  # pragma: no cover
        return f"{time_str.zfill(5)}:00"  # pragma: no cover

    # H:MM形式の場合
    if re.match(r"^\d{1}:\d{2}$", time_str):  # pragma: no cover
        return f"0{time_str}:00"  # pragma: no cover

    # その他の場合はデフォルト値を返す
    return "00:00:00"  # pragma: no cover


def unix_time_to_datetime(unix_time_ms):
    """UNIXタイム（ミリ秒）を 'yyyy/MM/dd HH:mm:ss' 形式に変換"""
    if unix_time_ms == 0:
        return ""

    # ミリ秒を秒に変換
    unix_time_sec = unix_time_ms / 1000

    # datetimeオブジェクトに変換
    dt = datetime.fromtimestamp(unix_time_sec)

    # 指定フォーマットで文字列に変換
    return dt.strftime("%Y/%m/%d %H:%M:%S")


def format_time_difference(time_diff):
    """timedeltaオブジェクトをHH:MM:SS形式に変換（24時間超過時は時間が積み上がる）"""
    total_seconds = int(time_diff.total_seconds())

    if total_seconds < 0:
        return "負の値"

    # 時間、分、秒を計算
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # HH:MM:SS形式で返す（時間は桁数制限なし、分と秒は2桁固定）
    return f"{hours}:{minutes:02d}:{seconds:02d}"
