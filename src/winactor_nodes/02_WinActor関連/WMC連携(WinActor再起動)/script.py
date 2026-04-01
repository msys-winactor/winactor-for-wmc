import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.winactors import put_winactors_restart


def main(**kwargs):
    # run関数の呼び出し
    return put_winactors_restart.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!        # type: ignore
    TOKEN = !アクセストークン!    # type: ignore
    WINACTOR_ID = !WinActorID!  # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not WINACTOR_ID or not str(WINACTOR_ID).strip():
        missing_params.append("WinActorID")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, winactor_id=WINACTOR_ID)
