import sys
import os

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.files import get_files_csv

def main(**kwargs):
    return get_files_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    CREATEDATTYPE = !登録日条件|次の範囲内,以後,以前!  # type: ignore
    CREATEDATDATE1 = !登録日1(yyyy/MM/dd)!  # type: ignore
    CREATEDATDATE2 = !登録日2(yyyy/MM/dd)!  # type: ignore
    UPDATEDATTYPE = !更新日条件|次の範囲内,以後,以前!  # type: ignore
    UPDATEDATDATE1 = !更新日1(yyyy/MM/dd)!  # type: ignore
    UPDATEDATDATE2 = !更新日2(yyyy/MM/dd)!  # type: ignore

    # 再代入
    if CREATEDATTYPE == "次の範囲内":
        CREATEDATTYPE = "range"
    elif CREATEDATTYPE == "以後":
        CREATEDATTYPE = "after"
    elif CREATEDATTYPE == "以前":
        CREATEDATTYPE = "before"

    if UPDATEDATTYPE == "次の範囲内":
        UPDATEDATTYPE = "range"
    elif UPDATEDATTYPE == "以後":
        UPDATEDATTYPE = "after"
    elif UPDATEDATTYPE == "以前":
        UPDATEDATTYPE = "before"

    # 値があるものだけparamsに入れる
    raw_params = {
        "encoding": ENCODING,
        "createdAtType": CREATEDATTYPE,
        "createdAtDate1": CREATEDATDATE1,
        "createdAtDate2": CREATEDATDATE2,
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