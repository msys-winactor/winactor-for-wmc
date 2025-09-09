from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    scenario_id = kwargs.get("scenario_id")
    scenario_data = kwargs.get("scenario_data") or {}

    # 所属名が渡されていればID変換
    department_name1 = kwargs.get("department_name1")
    department_name2 = kwargs.get("department_name2")
    department_name3 = kwargs.get("department_name3")

    # 3つすべて空欄の場合の既定値
    if not department_name1 and not department_name2 and not department_name3:
        scenario_data["department1"] = 0
        scenario_data["department2"] = None
        scenario_data["department3"] = None
    else:
        # 部門一覧取得
        departments_result = get_departments.get_departments(
            base_url=base_url, token=token
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
            scenario_data["department1"] = department1_id
        if department2_id is not None:
            scenario_data["department2"] = department2_id
        if department3_id is not None:
            scenario_data["department3"] = department3_id

    # シナリオ更新API呼び出し (PUT /scenarios/{id})
    client = WMCApiClient(base_url, token)
    endpoint = f"/scenarios/{scenario_id}"
    result = client.put(endpoint, data=scenario_data)
    return result
