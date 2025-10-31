import csv

from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_path = kwargs.get("file_path")
    encoding = kwargs.get("encoding", "UTF-8")  # デフォルトはUTF-8

    if not base_url or not token or not file_path:
        raise ValueError("base_url, token, file_path は必須です。")

    # エンコーディングの変換
    if encoding == "MS932":
        file_encoding = "shift_jis"
    elif encoding == "UTF-8":
        file_encoding = "utf-8-sig"  # BOM付きUTF-8でExcel対応
    else:
        file_encoding = "utf-8-sig"

    client = WMCApiClient(base_url, token)

    # 全ユーザー一覧を取得（ページングを考慮して全件取得）
    all_users = []
    page = 1
    page_size = 100

    while True:
        users_response = client.get("/users", params={"page": page, "size": page_size})
        users = users_response.get("items", [])

        if not users:
            break

        all_users.extend(users)

        # 最後のページかチェック
        if len(users) < page_size:
            break

        page += 1

    # CSVファイルを作成
    csv_data = []
    csv_data.append(["ユーザー名", "承認待ちスケジュールID", "承認待ちスケジュール名"])

    # 各ユーザーの承認待ちスケジュールを取得
    for user in all_users:
        user_id = user.get("id")
        user_name = user.get("name", "")

        if not user_id:
            continue

        try:
            # 承認待ちスケジュール一覧を取得
            approvals_response = client.get(f"/users/{user_id}/approvals")
            pending_schedules = approvals_response.get(
                "userPendingApprovalSchedules", []
            )

            # 承認待ちスケジュールが存在する場合のみCSVに追加
            for schedule in pending_schedules:
                schedule_id = schedule.get("id", "")
                schedule_name = schedule.get("name", "")
                csv_data.append([user_name, schedule_id, schedule_name])

        except Exception:
            # 個別ユーザーのエラーは無視して処理を続行
            continue

    # CSVファイルに書き込み
    with open(file_path, "w", newline="", encoding=file_encoding) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    return
