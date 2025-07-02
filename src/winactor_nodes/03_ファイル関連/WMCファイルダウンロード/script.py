import sys
import os

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

import get_files_content

# 各種パラメータ
BASE_URL = !BASE_URL!  # type: ignore
TOKEN = !TOKEN!  # type: ignore
FILE_ID = !ファイルID!  # type: ignore
SAVE_PATH = !保存ファイル名!  # type: ignore

# BASE_URLの末尾に「/」がなければ足す
if not BASE_URL.endswith("/"):
    BASE_URL += "/"
FILES_CONTENT_URL = BASE_URL + "files"

try:
    # 保存先ディレクトリがなければ作成
    save_dir = os.path.dirname(SAVE_PATH)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # ファイルをダウンロードして保存
    get_files_content.download_file_content(FILES_CONTENT_URL, TOKEN, FILE_ID, SAVE_PATH)

except Exception as e:
    raise winactor.WinActorError(1, f"ファイルダウンロードエラー\n{str(e)}")  # type: ignore