import sys
import os

sys.path.append(r"C:\Users\Public\msys-dx-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.users import get_users_approvals_csv

def main(**kwargs):
    # run関数の呼び出し
    return get_users_approvals_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    FILE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore

    # ディレクトリ作成
    save_dir = os.path.dirname(FILE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, file_path=FILE_PATH, encoding=ENCODING)