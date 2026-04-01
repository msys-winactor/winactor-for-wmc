import sys
import os

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.statistics import get_statistics_winactors_csv


def main(**kwargs):
    return get_statistics_winactors_csv.run(**kwargs)


if __name__ == "__main__":
    # WinActorから入力値を取得
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore

    # 追加: 部門条件（所属名）
    DEPARTMENT_NAME1 = !所属(親)!   # type: ignore
    DEPARTMENT_NAME2 = !所属(子)!   # type: ignore
    DEPARTMENT_NAME3 = !所属(孫)!   # type: ignore

    CSV_SAVE_PATH = !CSVファイル名!  # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not CSV_SAVE_PATH or not str(CSV_SAVE_PATH).strip():
        missing_params.append("CSVファイル名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

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

    # 正規化用
    def _norm(v):
        if isinstance(v, str):
            v = v.strip()
        return v

    # 値があるものだけ params に入れる
    raw_params = {
        "encoding": ENCODING,
        "periodAtType": PERIODATTYPE,
        "periodAtDate1": PERIODATDATE1,
        "periodAtDate2": PERIODATDATE2,

        # 追加: 所属名（モジュール側で ID に変換）
        "department_name1": _norm(DEPARTMENT_NAME1),
        "department_name2": _norm(DEPARTMENT_NAME2),
        "department_name3": _norm(DEPARTMENT_NAME3),
    }

    # 特例: 親=「共有」かつ 子/孫が空欄なら、ID 0 を直接指定して名称キーを削除
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