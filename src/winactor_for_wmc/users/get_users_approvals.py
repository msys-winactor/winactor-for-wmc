from winactor_for_wmc.common import user_utils
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    user_name = kwargs.get("user_name")

    # ユーザ名からユーザIDを取得
    user_id = user_utils.get_user_id_by_name(base_url, token, user_name)

    endpoint = f"/users/{user_id}/approvals"
    client = WMCApiClient(base_url, token)
    response = client.get(endpoint)
    return response


def get_schedule_info(result, index=0):
    """
    スケジュール一覧APIのレスポンスから指定インデックスの
    スケジュールIDと名前を取り出す
    - index: 0始まり。負のインデックス可（Python準拠）
    - 不正値や範囲外、データなしの場合は ("", "") を返す
    """
    schedules = (
        result.get("userPendingApprovalSchedules", [])
        if isinstance(result, dict)
        else []
    )

    try:
        idx = int(index)
    except (TypeError, ValueError):
        return "", ""

    if not schedules:
        return "", ""

    if idx < -len(schedules) or idx >= len(schedules):
        return "", ""

    target = schedules[idx]
    return target.get("id", ""), target.get("name", "")
