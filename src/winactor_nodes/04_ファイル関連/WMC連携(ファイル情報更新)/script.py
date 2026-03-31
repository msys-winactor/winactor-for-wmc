import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.files import put_files_info


def main(**kwargs):
    return put_files_info.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    FILE_ID = !ファイルID!  # type: ignore

    NAME = !更新後のファイル名!  # type: ignore
    FILETAG = !更新後のファイルタグ!  # type: ignore
    DESCRIPTION = !更新後のファイル説明!  # type: ignore

    # リクエストボディ作成（未入力は送らない）
    file_data = {}
    if NAME and str(NAME).strip():
        file_data["name"] = str(NAME).strip()
    if FILETAG and str(FILETAG).strip():
        file_data["fileTag"] = str(FILETAG).strip()
    if DESCRIPTION and str(DESCRIPTION).strip():
        file_data["description"] = str(DESCRIPTION).strip()

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, file_id=FILE_ID, file_data=file_data)
