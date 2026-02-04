import sys
import os

sys.path.append(r"C:\Users\Public\msys-dx-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.statistics import get_statistics_winactors_csv

def main(**kwargs):
    return get_statistics_winactors_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    PERIODATTYPE = !取得期間|次の範囲内,以後,以前!  # type: ignore
    PERIODATDATE1 = !期間1(yyyy/MM/dd)!  # type: ignore
    PERIODATDATE2 = !期間2(yyyy/MM/dd)!  # type: ignore

    # 再代入
    if PERIODATTYPE == "次の範囲内":
        PERIODATTYPE = "range"
    elif PERIODATTYPE == "以後":
        PERIODATTYPE = "after"
    elif PERIODATTYPE == "以前":
        PERIODATTYPE = "before"

    # 値があるものだけparamsに入れる
    raw_params = {
        "encoding": ENCODING,
        "periodAtType": PERIODATTYPE,
        "periodAtDate1": PERIODATDATE1,
        "periodAtDate2": PERIODATDATE2,
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