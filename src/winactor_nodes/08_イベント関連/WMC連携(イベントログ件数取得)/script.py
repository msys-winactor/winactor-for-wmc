import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.events import get_events_number


def main(**kwargs):
    return get_events_number.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!        # type: ignore
    TOKEN = !アクセストークン!    # type: ignore

    # 部門条件（所属名のみを受け取り、モジュール側で所属IDへ変換）
    DEPARTMENT_NAME1 = !所属(親)!   # type: ignore
    DEPARTMENT_NAME2 = !所属(子)!   # type: ignore
    DEPARTMENT_NAME3 = !所属(孫)!   # type: ignore

    # 日本語選択肢を API 指定値へ変換
    CREATED_AT_TYPE = !登録日時条件|次の範囲内,以後,以前!  # type: ignore
    if CREATED_AT_TYPE == "次の範囲内":
        CREATED_AT_TYPE = "range"
    elif CREATED_AT_TYPE == "以後":
        CREATED_AT_TYPE = "after"
    elif CREATED_AT_TYPE == "以前":
        CREATED_AT_TYPE = "before"

    # 日時条件
    CREATED_AT_DATE1 = !登録日時1(yyyy/MM/dd)!  # type: ignore
    CREATED_AT_TIME1 = !登録時刻1(hh:mm:ss)!    # type: ignore
    CREATED_AT_DATE2 = !登録日時2(yyyy/MM/dd)!  # type: ignore
    CREATED_AT_TIME2 = !登録時刻2(hh:mm:ss)!    # type: ignore

    # 配列条件（カンマ区切り/単一でも可）
    LEVELS = !重要度(0~3)!              # 例: "0,1,3" も可  # type: ignore
    LABELS = !イベントラベル!            # 例: "10,20" も可  # type: ignore
    WACT_IDS = !検索WinActorID!         # 例: "wa001,wa002"  # type: ignore

    # メッセージ条件
    MESSAGE_TYPE = !メッセージ検索条件|完全一致,部分一致,AND/NOT検索!  # type: ignore
    if MESSAGE_TYPE == "完全一致":
        MESSAGE_TYPE = "perfect"
    elif MESSAGE_TYPE == "部分一致":
        MESSAGE_TYPE = "partial"
    elif MESSAGE_TYPE == "AND/NOT検索":
        MESSAGE_TYPE = "andnot"

    MESSAGE = !メッセージ!  # type: ignore

    # ソート・ページング（PAGE は渡さず、SIZE は固定 100）
    SORT = !ソート項目|登録日時,重要度,メッセージ!  # type: ignore
    if SORT == "登録日時":
        SORT = "createdAt"
    elif SORT == "重要度":
        SORT = "level"
    elif SORT == "メッセージ":
        SORT = "message"

    SORT_DIR = !ソート方向|降順,昇順!  # type: ignore
    if SORT_DIR == "降順":
        SORT_DIR = "desc"
    elif SORT_DIR == "昇順":
        SORT_DIR = "asc"

    SIZE = 100  # 取得件数は固定

    # 値があるものだけ params に入れる（前後空白は除去）
    def _norm(v):
        if isinstance(v, str):
            v = v.strip()
        return v

    raw_params = {
        # 所属は名称のみ。ID指定は受け取らない。モジュール側で名称→ID変換
        "department_name1": _norm(DEPARTMENT_NAME1),
        "department_name2": _norm(DEPARTMENT_NAME2),
        "department_name3": _norm(DEPARTMENT_NAME3),

        "createdAtType": _norm(CREATED_AT_TYPE),
        "createdAtDate1": _norm(CREATED_AT_DATE1),
        "createdAtTime1": _norm(CREATED_AT_TIME1),
        "createdAtDate2": _norm(CREATED_AT_DATE2),
        "createdAtTime2": _norm(CREATED_AT_TIME2),

        # 配列系（run 側で list 化されるため、ここでは文字列のままでもOK）
        "level[]": _norm(LEVELS),
        "label[]": _norm(LABELS),
        "winactorId[]": _norm(WACT_IDS),

        "messageType": _norm(MESSAGE_TYPE),
        "message": _norm(MESSAGE),
        "sort": _norm(SORT),
        "sortDirection": _norm(SORT_DIR),
        # "page" は渡さない
        "size": SIZE,  # 固定値
    }

    # 特例: 親=「共有」かつ 子/孫が空欄なら、ID 0 に置換し名称キーを削除して変換処理をスキップ
    dn1 = _norm(DEPARTMENT_NAME1)
    dn2 = _norm(DEPARTMENT_NAME2)
    dn3 = _norm(DEPARTMENT_NAME3)
    if (dn1 == "共有") and (not dn2) and (not dn3):
        raw_params["department1"] = 0  # 数値 0 を設定
        # 名称キーは渡さない（モジュール側の名称→ID変換を確実にスキップする）
        raw_params.pop("department_name1", None)
        raw_params.pop("department_name2", None)
        raw_params.pop("department_name3", None)

    params = {k: v for k, v in raw_params.items() if v not in (None, "", [])}

    # 実行（params はトップレベル kwargs として渡す）
    result = main(base_url=BASE_URL, token=TOKEN, **params)

    # 総件数のみ取得
    total = get_events_number.get_number(result)

    # 取得結果を WinActor 変数に格納
    winactor.set_variable($総件数$, total)  # type: ignore
