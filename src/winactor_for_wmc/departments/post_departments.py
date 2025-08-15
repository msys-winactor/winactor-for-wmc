from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    department_data = kwargs.get("department_data") or {}

    # 入力された所属名（前後空白を除去）
    raw_parent = kwargs.get("department_name1")  # 親所属名
    raw_child = kwargs.get("department_name2")  # 子所属名
    parent_name = str(raw_parent).strip() if raw_parent else ""
    child_name = str(raw_child).strip() if raw_child else ""

    # ルール:
    # - 親/子が未入力 → 新規所属は「親」（階層IDなし）
    # - 親のみ入力 → 新規所属は「子」（department1 を設定）
    # - 親・子を入力 → 新規所属は「孫」（department1, department2 を設定）
    parent_id = None
    child_id = None

    if parent_name:
        departments_result = get_departments.get_departments(
            base_url=base_url, token=token
        )
        parent_id, child_id, _ = get_departments.get_departments_ids_by_names(
            departments_result,
            department_name1=parent_name,
            department_name2=child_name or None,
            department_name3=None,
        )

    # 親のみ入力: 子として登録（department1）
    if parent_name and (parent_id is not None):
        department_data["department1"] = parent_id

    # 親・子入力: 孫として登録（department1, department2）
    if parent_name and child_name and (child_id is not None):
        department_data["department2"] = child_id

    # 所属登録API呼び出し
    client = WMCApiClient(base_url, token)
    endpoint = "/departments"
    result = client.post(endpoint, data=department_data)
    return result
