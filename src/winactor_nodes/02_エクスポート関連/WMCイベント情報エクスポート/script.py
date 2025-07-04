import sys
import os

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.events import export_csv

def main(**kwargs):
    return export_csv.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !BASE_URL!  # type: ignore
    TOKEN = !TOKEN!  # type: ignore
    CSV_SAVE_PATH = !CSV_SAVE_PATH!  # type: ignore
    ENCODING = !ENCODING!  # type: ignore
    CREATED_AT_TYPE = !CREATED_AT_TYPE!  # type: ignore
    CREATED_AT_DATE1 = !CREATED_AT_DATE1!  # type: ignore
    CREATED_AT_DATE2 = !CREATED_AT_DATE2!  # type: ignore

    params = {
        "encoding": ENCODING,
        "createdAtType": CREATED_AT_TYPE,
        "createdAtDate1": CREATED_AT_DATE1,
        "createdAtDate2": CREATED_AT_DATE2,
    }

    save_dir = os.path.dirname(CSV_SAVE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        save_path=CSV_SAVE_PATH,
        params=params,
    )