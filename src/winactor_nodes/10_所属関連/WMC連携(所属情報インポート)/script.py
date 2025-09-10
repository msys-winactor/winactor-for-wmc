import sys
import os

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.departments import post_departments_csv

# 各種パラメータ
BASE_URL = !WMC URL!  # type: ignore
TOKEN = !アクセストークン!  # type: ignore
CSV_FILE_PATH = !CSVファイル名!  # type: ignore
ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
EXECUTE_TYPE = !処理区分|新規登録,更新,削除!  # type: ignore

def main(**kwargs):
    return post_departments_csv.run(**kwargs)

if __name__ == "__main__":
    # パラメータ整形
    import_data = {}
    
    # 再代入
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