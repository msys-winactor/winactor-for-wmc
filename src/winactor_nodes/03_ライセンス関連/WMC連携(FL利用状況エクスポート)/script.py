import sys
import os

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.licenses import get_licenses_usage_csv

def main(**kwargs):
    # run関数の呼び出し
    return get_licenses_usage_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    FILE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    CREATED_AT_TYPE = !検索条件|次の範囲内,以後,以前!  # type: ignore
    START_DATE = !検索日1(yyyy/MM/dd)!  # type: ignore
    START_TIME = !検索時刻1(hh:mm:ss)!  # type: ignore
    END_DATE = !検索日2(yyyy/MM/dd)!  # type: ignore
    END_TIME = !検索時刻2(hh:mm:ss)!  # type: ignore

    # 再代入
    if CREATED_AT_TYPE == "次の範囲内":
        CREATED_AT_TYPE = "range"
    elif CREATED_AT_TYPE == "以後":
        CREATED_AT_TYPE = "after"
    elif CREATED_AT_TYPE == "以前":
        CREATED_AT_TYPE = "before"

    # ディレクトリ作成
    save_dir = os.path.dirname(FILE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    # mainの呼び出し
    result = main(
        base_url=BASE_URL, 
        token=TOKEN, 
        file_path=FILE_PATH, 
        encoding=ENCODING,
        created_at_type=CREATED_AT_TYPE,
        start_date=START_DATE,
        end_date=END_DATE,
        start_time=START_TIME,
        end_time=END_TIME
    )