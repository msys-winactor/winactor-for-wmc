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


def _ensure_index_provided(index, name):
    if index is None:
        raise ValueError(f"{name} が未指定です。")
    if isinstance(index, str) and index.strip() == "":
        raise ValueError(f"{name} が未指定です。")


def get_schedule_info(result, index=0):
    """
    スケジュール一覧APIのレスポンスから指定インデックスの
    スケジュールIDと名前を取り出す
    - index: 0始まり。負のインデックス可（Python準拠）
    - 不正値や範囲外、データなしの場合は例外を送出
    """
    _ensure_index_provided(index, "スケジュールのインデックス")

    if not isinstance(result, dict):
        raise ValueError("APIレスポンスが不正です（dict ではありません）。")

    schedules = result.get("userPendingApprovalSchedules")
    if not isinstance(schedules, list) or len(schedules) == 0:
        raise ValueError("スケジュール情報が存在しません。")

    try:
        idx = int(index)
    except (TypeError, ValueError):
        raise ValueError("スケジュールのインデックスが数値ではありません。")

    if idx < -len(schedules) or idx >= len(schedules):
        raise ValueError("スケジュールのインデックスが範囲外です。")

    target = schedules[idx] or {}
    return target.get("id", "") or "", target.get("name", "") or ""
