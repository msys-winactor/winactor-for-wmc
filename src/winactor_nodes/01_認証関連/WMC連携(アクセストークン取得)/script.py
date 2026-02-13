import sys

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.auth import get_token

def main(**kwargs):
    # run関数の呼び出し
    return get_token.run(**kwargs)


if __name__ == "__main__":
    # WinActorから入力値を取得
    base_url = !WMC URL!     # pyright: ignore
    user_id = !ユーザ名!     # pyright: ignore
    password = !パスワード!    # pyright: ignore

    # mainの呼び出し
    result = main(base_url=base_url, user_id=user_id, password=password)

    # 結果をWinActorへ返す
    winactor.set_variable($アクセストークン$, result.get("token", ""))   # pyright: ignore
