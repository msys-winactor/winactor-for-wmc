from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_path = kwargs.get("file_path")
    file_data = kwargs.get("file_data")
    department_name1 = kwargs.get("department_name1")
    department_name2 = kwargs.get("department_name2")
    department_name3 = kwargs.get("department_name3")

    # 1. 部門名→ID変換
    departments_result = get_departments.get_departments(base_url=base_url, token=token)
    department1_id, department2_id, department3_id = (
        get_departments.get_departments_ids_by_names(
            departments_result,
            department_name1=department_name1,
            department_name2=department_name2,
            department_name3=department_name3,
        )
    )
    if department1_id is not None:
        file_data["department1"] = department1_id
    if department2_id is not None:
        file_data["department2"] = department2_id
    if department3_id is not None:
        file_data["department3"] = department3_id

    # 2. ファイルアップロードAPI呼び出し
    client = WMCApiClient(base_url, token)
    endpoint = "/files"
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = client.post(endpoint, data=file_data, files=files)
        return response.get("id")
