import sys
import os

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.events import get_events_csv

def main(**kwargs):
    return get_events_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    CREATED_AT_TYPE = !条件|次の範囲内,以後,以前!  # type: ignore
    CREATED_AT_DATE1 = !日付指定1(yyyy/MM/dd)!  # type: ignore
    CREATED_AT_DATE2 = !日付指定2(yyyy/MM/dd)!  # type: ignore

    # 再代入
    if CREATED_AT_TYPE == "次の範囲内":
        CREATED_AT_TYPE = "range"
    elif CREATED_AT_TYPE == "以後":
        CREATED_AT_TYPE = "after"
    elif CREATED_AT_TYPE == "以前":
        CREATED_AT_TYPE = "before"

    # 値があるものだけparamsに入れる
    raw_params = {
        "encoding": ENCODING,
        "createdAtType": CREATED_AT_TYPE,
        "createdAtDate1": CREATED_AT_DATE1,
        "createdAtDate2": CREATED_AT_DATE2,
    }
    params = {k: v for k, v in raw_params.items() if v not in (None, "", [])}


    save_dir = os.path.dirname(CSV_SAVE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        save_path=CSV_SAVE_PATH,
        params=params,
    )
