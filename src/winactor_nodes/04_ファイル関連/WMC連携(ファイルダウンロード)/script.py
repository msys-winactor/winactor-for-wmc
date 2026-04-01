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
    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not FILE_ID or not str(FILE_ID).strip():
        missing_params.append("ファイルID")
    if not SAVE_PATH or not str(SAVE_PATH).strip():
        missing_params.append("保存ファイル名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

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
