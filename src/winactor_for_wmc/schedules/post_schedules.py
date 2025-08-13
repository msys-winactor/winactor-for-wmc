from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    schedules_url = kwargs.get("schedules_url")
    departments_url = kwargs.get("departments_url")
    token = kwargs.get("token")
    schedule_data = kwargs.get("schedule_data")
    department_name1 = kwargs.get("department_name1")
    department_name2 = kwargs.get("department_name2")
    department_name3 = kwargs.get("department_name3")

    # 1. 部門名→ID変換
    departments_result = get_departments.get_departments(
        base_url=departments_url, token=token
    )
    department1_id, department2_id, department3_id = (
        get_departments.get_departments_ids_by_names(
            departments_result,
            department_name1=department_name1,
            department_name2=department_name2,
            department_name3=department_name3,
        )
    )
    if department1_id is not None:
        schedule_data["department1"] = department1_id
    if department2_id is not None:
        schedule_data["department2"] = department2_id
    if department3_id is not None:
        schedule_data["department3"] = department3_id

    # 2. スケジュール登録API呼び出し
    endpoint = "/schedules"
    client = WMCApiClient(schedules_url, token)
    return client.post(endpoint, data=schedule_data)
