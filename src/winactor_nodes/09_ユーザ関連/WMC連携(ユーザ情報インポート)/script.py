import sys
import os

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.users import post_users_csv

# 各種パラメータ
BASE_URL = !*WMC URL!  # type: ignore
TOKEN = !*アクセストークン!  # type: ignore
CSV_FILE_PATH = !*CSVファイル名!  # type: ignore
ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
EXECUTE_TYPE = !処理区分|新規登録,更新,削除!  # type: ignore

def main(**kwargs):
    return post_users_csv.run(**kwargs)

if __name__ == "__main__":
    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not CSV_FILE_PATH or not str(CSV_FILE_PATH).strip():
        missing_params.append("CSVファイル名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # パラメータ整形
    import_data = {}
    
    # 処理区分の変換
    if EXECUTE_TYPE == "新規登録":
        EXECUTE_TYPE = "I"
    elif EXECUTE_TYPE == "更新":
        EXECUTE_TYPE = "U"
    elif EXECUTE_TYPE == "削除":
        EXECUTE_TYPE = "D"

    if ENCODING:
        ENCODING = ENCODING.strip()
        if ENCODING:
            import_data["encoding"] = ENCODING
    
    if EXECUTE_TYPE:
        EXECUTE_TYPE = EXECUTE_TYPE.strip()
        if EXECUTE_TYPE:
            import_data["executeType"] = EXECUTE_TYPE
    
    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        csv_file_path=CSV_FILE_PATH,
        import_data=import_data,
    )
