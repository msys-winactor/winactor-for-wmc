import sys
import os

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.tasks import get_tasks_csv


def main(**kwargs):
    return get_tasks_csv.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore

    # 追加: 部門条件（所属名のみを受け取り、モジュール側で所属IDへ変換）
    DEPARTMENT_NAME1 = !所属(親)!   # type: ignore
    DEPARTMENT_NAME2 = !所属(子)!   # type: ignore
    DEPARTMENT_NAME3 = !所属(孫)!   # type: ignore

    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore
    ENCODING = !エンコーディング|MS932,UTF-8!  # type: ignore
    CREATEDATTYPE = !生成日条件|次の範囲内,以後,以前!  # type: ignore
    CREATEDATDATE1 = !生成日1(yyyy/MM/dd)!  # type: ignore
    CREATEDATDATE2 = !生成日2(yyyy/MM/dd)!  # type: ignore
    STARTEDATTYPE = !開始日条件|次の範囲内,以後,以前!  # type: ignore
    STARTEDATDATE1 = !開始日1(yyyy/MM/dd)!  # type: ignore
    STARTEDATDATE2 = !開始日2(yyyy/MM/dd)!  # type: ignore
    FINISHEDATTYPE = !終了日条件|次の範囲内,以後,以前!  # type: ignore
    FINISHEDATDATE1 = !終了日1(yyyy/MM/dd)!  # type: ignore
    FINISHEDATDATE2 = !終了日2(yyyy/MM/dd)!  # type: ignore
    UPDATEDATTYPE = !更新日条件|次の範囲内,以後,以前!  # type: ignore
    UPDATEDATDATE1 = !更新日1(yyyy/MM/dd)!  # type: ignore
    UPDATEDATDATE2 = !更新日2(yyyy/MM/dd)!  # type: ignore
    SCHEDULEDATTYPE = !実行予定日条件|次の範囲内,以後,以前!  # type: ignore
    SCHEDULEDATDATE1 = !実行予定日1(yyyy/MM/dd)!  # type: ignore
    SCHEDULEDATDATE2 = !実行予定日2(yyyy/MM/dd)!  # type: ignore

    # 再代入
    if CREATEDATTYPE == "次の範囲内":
        CREATEDATTYPE = "range"
    elif CREATEDATTYPE == "以後":
        CREATEDATTYPE = "after"
    elif CREATEDATTYPE == "以前":
        CREATEDATTYPE = "before"

    if STARTEDATTYPE == "次の範囲内":
        STARTEDATTYPE = "range"
    elif STARTEDATTYPE == "以後":
        STARTEDATTYPE = "after"
    elif STARTEDATTYPE == "以前":
        STARTEDATTYPE = "before"

    if FINISHEDATTYPE == "次の範囲内":
        FINISHEDATTYPE = "range"
    elif FINISHEDATTYPE == "以後":
        FINISHEDATTYPE = "after"
    elif FINISHEDATTYPE == "以前":
        FINISHEDATTYPE = "before"

    if UPDATEDATTYPE == "次の範囲内":
        UPDATEDATTYPE = "range"
    elif UPDATEDATTYPE == "以後":
        UPDATEDATTYPE = "after"
    elif UPDATEDATTYPE == "以前":
        UPDATEDATTYPE = "before"

    if SCHEDULEDATTYPE == "次の範囲内":
        SCHEDULEDATTYPE = "range"
    elif SCHEDULEDATTYPE == "以後":
        SCHEDULEDATTYPE = "after"
    elif SCHEDULEDATTYPE == "以前":
        SCHEDULEDATTYPE = "before"

    # 正規化
    def _norm(v):
        if isinstance(v, str):
            v = v.strip()
        return v

    # 値があるものだけ params に入れる
    raw_params = {
        "encoding": ENCODING,
        "createdAtType": CREATEDATTYPE,
        "createdAtDate1": CREATEDATDATE1,
        "createdAtDate2": CREATEDATDATE2,
        "startedAtType": STARTEDATTYPE,
        "startedAtDate1": STARTEDATDATE1,
        "startedAtDate2": STARTEDATDATE2,
        "finishedAtType": FINISHEDATTYPE,
        "finishedAtDate1": FINISHEDATDATE1,
        "finishedAtDate2": FINISHEDATDATE2,
        "updatedAtType": UPDATEDATTYPE,
        "updatedAtDate1": UPDATEDATDATE1,
        "updatedAtDate2": UPDATEDATDATE2,
        "scheduledAtType": SCHEDULEDATTYPE,
        "scheduledAtDate1": SCHEDULEDATDATE1,
        "scheduledAtDate2": SCHEDULEDATDATE2,

        # 追加: 所属名（モジュール側で ID に変換）
        "department_name1": _norm(DEPARTMENT_NAME1),
        "department_name2": _norm(DEPARTMENT_NAME2),
        "department_name3": _norm(DEPARTMENT_NAME3),
    }

    # 特例: 親=「共有」かつ 子/孫が空欄なら、ID 0 を設定し名称キーを削除
    dn1 = _norm(DEPARTMENT_NAME1)
    dn2 = _norm(DEPARTMENT_NAME2)
    dn3 = _norm(DEPARTMENT_NAME3)
    if (dn1 == "共有") and (not dn2) and (not dn3):
        raw_params["department1"] = 0
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