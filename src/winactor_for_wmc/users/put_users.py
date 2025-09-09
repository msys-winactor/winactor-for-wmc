from winactor_for_wmc.common import get_departments, user_utils
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    user_name = kwargs.get("user_name")
    user_data = kwargs.get("user_data") or {}

    if not user_name:
        raise ValueError("user_name is required")

    # ユーザ名からユーザIDを取得
    user_id = user_utils.get_user_id_by_name(base_url, token, user_name)

    # 所属名が渡されていればID変換
    department_name1 = kwargs.get("department_name1")
    department_name2 = kwargs.get("department_name2")
    department_name3 = kwargs.get("department_name3")

    # 3つすべて空欄の場合の既定値（所属を「未所属」にリセット）
    if not department_name1 and not department_name2 and not department_name3:
        user_data["department1"] = 0
        user_data["department2"] = None
        user_data["department3"] = None
    else:
        # 部門一覧取得して名称→ID変換
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

    # ユーザ更新API呼び出し（正常時はレスポンスボディなし）
    client = WMCApiClient(base_url, token)
    endpoint = f"/users/{user_id}"
    result = client.put(endpoint, data=user_data)
    return result
