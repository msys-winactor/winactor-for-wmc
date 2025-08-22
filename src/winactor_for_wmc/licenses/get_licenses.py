from winactor_for_wmc.common import user_utils
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    user_name = kwargs.get("user_name")

    # 必ずuser_nameからuser_idを取得
    user_id = user_utils.get_user_id_by_name(base_url, token, user_name)

    endpoint = f"/users/{user_id}/approvals"
    client = WMCApiClient(base_url, token)
    response = client.get(endpoint)
    return response


def get_first_schedule_info(result):
    """
    スケジュール一覧APIのレスポンスから最初のスケジュールIDと名前を取り出す
    """
    schedules = (
        result.get("userPendingApprovalSchedules", [])
        if isinstance(result, dict)
        else []
    )
    if schedules:
        first_schedule = schedules[0]
        schedule_id = first_schedule.get("id", "")
        schedule_name = first_schedule.get("name", "")
    else:
        schedule_id = ""
        schedule_name = ""
    return schedule_id, schedule_name
