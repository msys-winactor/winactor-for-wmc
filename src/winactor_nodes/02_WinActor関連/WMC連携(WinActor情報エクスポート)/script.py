import sys
import os

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.winactors import get_winactors_csv

def main(**kwargs):
    return get_winactors_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    UPDATEDATTYPE = !条件|次の範囲内,以後,以前!  # type: ignore
    UPDATEDATDATE1 = !更新日1(yyyy/MM/dd)!  # type: ignore
    UPDATEDATDATE2 = !更新日2(yyyy/MM/dd)!  # type: ignore

    # 再代入
    if UPDATEDATTYPE == "次の範囲内":
        UPDATEDATTYPE = "range"
    elif UPDATEDATTYPE == "以後":
        UPDATEDATTYPE = "after"
    elif UPDATEDATTYPE == "以前":
        UPDATEDATTYPE = "before"

    # 値があるものだけparamsに入れる
    raw_params = {
        "encoding": ENCODING,
        "updatedAtType": UPDATEDATTYPE,
        "updatedAtDate1": UPDATEDATDATE1,
        "updatedAtDate2": UPDATEDATDATE2,
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
