import sys
import os

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.schedules import get_schedules_csv


def main(**kwargs):
    return get_schedules_csv.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore

    # 追加: 部門条件（所属名のみを受け取り、モジュール側で所属IDへ変換）
    DEPARTMENT_NAME1 = !所属(親)!   # type: ignore
    DEPARTMENT_NAME2 = !所属(子)!   # type: ignore
    DEPARTMENT_NAME3 = !所属(孫)!   # type: ignore

    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    UPDATEDATTYPE = !更新日条件|次の範囲内,以後,以前!  # type: ignore
    UPDATEDATDATE1 = !更新日1(yyyy/MM/dd)!  # type: ignore
    UPDATEDATDATE2 = !更新日2(yyyy/MM/dd)!  # type: ignore

    # 再代入
    if UPDATEDATTYPE == "次の範囲内":
        UPDATEDATTYPE = "range"
    elif UPDATEDATTYPE == "以後":
        UPDATEDATTYPE = "after"
    elif UPDATEDATTYPE == "以前":
        UPDATEDATTYPE = "before"

    # 値があるものだけ params に入れるための正規化
    def _norm(v):
        if isinstance(v, str):
            v = v.strip()
        return v

    # 値があるものだけ params に入れる（元の項目は変更なし）
    raw_params = {
        "encoding": ENCODING,
        "updatedAtType": UPDATEDATTYPE,
        "updatedAtDate1": UPDATEDATDATE1,
        "updatedAtDate2": UPDATEDATDATE2,

        # 追加: 所属名（モジュール側で ID へ変換するために渡す）
        "department_name1": _norm(DEPARTMENT_NAME1),
        "department_name2": _norm(DEPARTMENT_NAME2),
        "department_name3": _norm(DEPARTMENT_NAME3),
    }

    # 特例: 親=「共有」かつ 子/孫が空欄なら、ID 0 に置換し名称キーを削除して変換処理をスキップ
    dn1 = _norm(DEPARTMENT_NAME1)
    dn2 = _norm(DEPARTMENT_NAME2)
    dn3 = _norm(DEPARTMENT_NAME3)
    if (dn1 == "共有") and (not dn2) and (not dn3):
        raw_params["department1"] = 0  # 数値 0 を設定
        raw_params.pop("department_name1", None)
        raw_params.pop("department_name2", None)
        raw_params.pop("department_name3", None)

    params = {k: v for k, v in raw_params.items() if v not in (None, "", [])}

    save_dir = os.path.dirname(CSV_SAVE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        save_path=CSV_SAVE_PATH,
        params=params,
    )