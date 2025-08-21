import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.files import put_files_info


def main(**kwargs):
    return put_files_info.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    FILE_ID = !ファイルID!  # type: ignore

    FROMHISTORYID = !FROMHISTORYID!  # type: ignore
    FILE_PATH = !ファイル名!  # type: ignore
    DESCRIPTION = !説明!  # type: ignore

    # リクエストボディ作成（未入力は送らない）
    file_data = {}


    
    #if FROMHISTORYID and str(FROMHISTORYID).strip():
    #    file_data["fromHistoryId"] = str(FROMHISTORYID).strip()

    if FROMHISTORYID is not None and str(FROMHISTORYID).strip():
        file_data["fromHistoryId"] = int(str(FROMHISTORYID).strip())

    if DESCRIPTION and str(DESCRIPTION).strip():
        file_data["description"] = str(DESCRIPTION).strip()


    import ctypes
    import json

        # ここでポップアップ表示
    ctypes.windll.user32.MessageBoxW(
            0, f"file_data: {json.dumps(file_data)}", "デバッグ表示", 0
        )
        # ここまで



    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, file_id=FILE_ID, file_path=FILE_PATH, file_data=file_data)