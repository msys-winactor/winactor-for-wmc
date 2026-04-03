import sys
import os

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.users import get_users_approvals_csv

def main(**kwargs):
    # run関数の呼び出し
    return get_users_approvals_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !*WMC URL!  # type: ignore
    TOKEN = !*アクセストークン!  # type: ignore
    FILE_PATH = !*CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not FILE_PATH or not str(FILE_PATH).strip():
        missing_params.append("CSVファイル名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # ディレクトリ作成
    save_dir = os.path.dirname(FILE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, file_path=FILE_PATH, encoding=ENCODING)
