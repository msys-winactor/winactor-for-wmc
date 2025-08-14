# winactor_for_wmc/users/post_users.py
from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    user_data = kwargs.get("user_data") or {}

    # 所属名が渡されていればID変換
    department_name1 = kwargs.get("department_name1")
    department_name2 = kwargs.get("department_name2")
    department_name3 = kwargs.get("department_name3")

    if department_name1 or department_name2 or department_name3:
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
            user_data["department1"] = department1_id
        if department2_id is not None:
            user_data["department2"] = department2_id
        if department3_id is not None:
            user_data["department3"] = department3_id

    # ユーザ登録API呼び出し
    client = WMCApiClient(base_url, token)
    endpoint = "/users"
    result = client.post(endpoint, data=user_data)
    return result
