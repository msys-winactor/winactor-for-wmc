import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.files import put_files_info


def main(**kwargs):
    return put_files_info.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !*WMC URL!  # type: ignore
    TOKEN = !*アクセストークン!  # type: ignore
    FILE_ID = !*ファイルID!  # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not FILE_ID or not str(FILE_ID).strip():
        missing_params.append("ファイルID")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

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
