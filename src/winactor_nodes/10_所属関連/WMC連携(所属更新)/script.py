import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.departments import put_departments


def main(**kwargs):
    return put_departments.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    DEPARTMENT_ID = !所属ID!  # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not DEPARTMENT_ID or not str(DEPARTMENT_ID).strip():
        missing_params.append("所属ID")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    NAME = !更新後の所属名!  # type: ignore
    REMARKS = !更新後のメモ!  # type: ignore

    # リクエストボディ作成（未入力は送らない）
    department_data = {}
    if NAME and str(NAME).strip():
        department_data["name"] = str(NAME).strip()
    if REMARKS and str(REMARKS).strip():
        department_data["remarks"] = str(REMARKS).strip()

    # mainの呼び出し
    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        department_id=DEPARTMENT_ID,
        department_data=department_data,
    )
