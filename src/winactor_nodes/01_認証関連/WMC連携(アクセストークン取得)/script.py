import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.auth import get_token

def main(**kwargs):
    # run関数の呼び出し
    return get_token.run(**kwargs)


if __name__ == "__main__":
    # WinActorから入力値を取得
    base_url = !WMC URL!     # pyright: ignore
    user_id = !ユーザ名!     # pyright: ignore
    password = !パスワード!    # pyright: ignore

    # 必須パラメータチェック
    missing_params = []
    if not base_url or not str(base_url).strip():
        missing_params.append("WMC URL")
    if not user_id or not str(user_id).strip():
        missing_params.append("ユーザ名")
    if not password or not str(password).strip():
        missing_params.append("パスワード")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # mainの呼び出し
    result = main(base_url=base_url, user_id=user_id, password=password)

    # 結果をWinActorへ返す
    winactor.set_variable($アクセストークン$, result.get("token", ""))   # pyright: ignore
