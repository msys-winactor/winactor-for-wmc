import sys
import os

# モジュール検索パスを追加
sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.auth import get_access_token

def main(**kwargs):
    return get_access_token.run(**kwargs)

if __name__ == "__main__":
    # WinActorからの入力（仮変数、WinActorで指定された変数名に応じて変更）
    base_url = !URL!            # pyright: ignore
    user_id = !ユーザーID!       # pyright: ignore
    password = !パスワード!      # pyright: ignore

    try:
        # 実行
        result = main(base_url=base_url, user_id=user_id, password=password)
        
        # 結果をWinActorへ返す
        winactor.set_variable($ステータス$, result.get("status", ""))   # pyright: ignore
        winactor.set_variable($トークン$, result.get("token", ""))     # pyright: ignore
        
    except Exception as e:
        raise winactor.WinActorError(1, str(e)) # pyright: ignore