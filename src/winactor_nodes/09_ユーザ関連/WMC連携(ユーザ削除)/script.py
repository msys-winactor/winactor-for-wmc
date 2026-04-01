import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.users import delete_users


def main(**kwargs):
    # run関数の呼び出し
    return delete_users.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !*WMC URL!  # type: ignore
    TOKEN = !*アクセストークン!  # type: ignore
    USER_NAME = !*ユーザ名!  # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not USER_NAME or not str(USER_NAME).strip():
        missing_params.append("ユーザ名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, user_name=USER_NAME)
