import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.departments import delete_departments


def main(**kwargs):
    # run関数の呼び出し
    return delete_departments.run(**kwargs)


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

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, department_id=DEPARTMENT_ID)
