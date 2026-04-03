import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.departments import post_departments


# 各種パラメータ
BASE_URL = !*WMC URL!  # type: ignore
TOKEN = !*アクセストークン!  # type: ignore
PARENT_DEPARTMENT = !追加先の所属(親)!  # type: ignore
CHILD_DEPARTMENT = !追加先の所属(子)!  # type: ignore
NAME = !*所属名!  # type: ignore
REMARKS = !メモ!  # type: ignore


def main(**kwargs):
    return post_departments.run(**kwargs)


if __name__ == "__main__":
    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not NAME or not str(NAME).strip():
        missing_params.append("所属名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    department_data = {}

    if NAME:
        _name = str(NAME).strip()
        if _name:
            department_data["name"] = _name

    if REMARKS:
        _remarks = str(REMARKS).strip()
        if _remarks:
            department_data["remarks"] = _remarks

    parent_name = str(PARENT_DEPARTMENT).strip() if PARENT_DEPARTMENT else None
    child_name = str(CHILD_DEPARTMENT).strip() if CHILD_DEPARTMENT else None

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        department_data=department_data,
        department_name1=parent_name,  # 親所属名（未入力なら親として登録）
        department_name2=child_name,   # 子所属名（親も入力時は孫として登録）
    )

    department_id = result.get("id", "")  # idが無い場合は空文字
    winactor.set_variable($所属ID$, department_id)  # type: ignore
