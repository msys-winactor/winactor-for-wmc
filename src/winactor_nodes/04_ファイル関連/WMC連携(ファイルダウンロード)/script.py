import sys
import os

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.files import get_files_content

# 各種パラメータ
BASE_URL = !WMC URL!  # type: ignore
TOKEN = !アクセストークン!  # type: ignore
FILE_ID = !ファイルID!  # type: ignore
SAVE_PATH = !保存ファイル名!  # type: ignore

def main(**kwargs):
    return get_files_content.run(**kwargs)

if __name__ == "__main__":
    # 保存先ディレクトリがなければ作成
    save_dir = os.path.dirname(SAVE_PATH)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # ファイルをダウンロードして保存
    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        file_id=FILE_ID,
        save_path=SAVE_PATH
    )
