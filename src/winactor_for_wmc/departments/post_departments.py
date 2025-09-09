from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def _norm(x):
    if x is None:
        return ""
    s = str(x).strip()
    return s


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    department_data = kwargs.get("department_data") or {}

    # 入力された所属名（前後空白を除去）
    parent_name = _norm(kwargs.get("department_name1"))
    child_name = _norm(kwargs.get("department_name2"))

    # ルール:
    # - 親/子が未入力 → 新規所属は「親」（階層IDなし）
    # - 親のみ入力 → 新規所属は「子」（department1 を設定）
    # - 親・子を入力 → 新規所属は「孫」（department1, department2 を設定）
    # 追加検証:
    # - 子のみ指定は不可（親が必須）
    # - 名前解決に失敗したら例外（get_departments.pyは変更しない前提）
    parent_id = None
    child_id = None

    # 子のみ指定はエラー
    if child_name and not parent_name:
        raise ValueError("子所属を指定する場合は親所属も指定してください。")

    if parent_name:
        # 所属一覧を取得して名称→ID 解決
        dep_result = get_departments.get_departments(base_url=base_url, token=token)
        resolved_parent_id, resolved_child_id, _ = (
            get_departments.get_departments_ids_by_names(
                dep_result,
                department_name1=parent_name,
                department_name2=(child_name or None),
                department_name3=None,
            )
        )

        parent_id = resolved_parent_id
        child_id = resolved_child_id

        # 親が見つからない場合はエラー
        if parent_id is None:
            raise ValueError(f"親所属が見つかりません: department_name1={parent_name}")

        # 親・子とも指定されているのに子が見つからない場合はエラー
        if child_name and (child_id is None):
            raise ValueError(
                f"子所属が見つかりません: department_name2={child_name}（親: {parent_name}）"
            )

        # 親のみ指定: 子として登録（department1）
        department_data["department1"] = parent_id

        # 親・子入力: 孫として登録（department1, department2）
        if child_name:
            department_data["department2"] = child_id

    # 親/子とも未入力なら最上位（親）として登録 → department1/2 の指定はしない

    # 所属登録API呼び出し
    client = WMCApiClient(base_url, token)
    endpoint = "/departments"
    result = client.post(endpoint, data=department_data)
    return result
