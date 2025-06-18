import sys
import os

# モジュール検索パスを追加
sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from template_python import sample_module

def main(**kwargs):
    return sample_module.run(**kwargs)


if __name__ == "__main__":
    # WinActorから入力値を取得
    user_id = !ユーザーID!     # pyright: ignore
    password = !パスワード!    # pyright: ignore

    # mainの呼び出し
    result = main(user_id=user_id, password=password)

    # 結果をWinActorに返す
    winactor.set_variable($ステータス$, result["status"])   # pyright: ignore
    winactor.set_variable($トークン$, result["token"])   # pyright: ignore
