import sys
import datetime

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.events import get_events

def unix_to_datetime(unix_time):
    """
    UNIXタイムをyyyy/mm/dd hh:mm:ss形式に変換
    """
    if unix_time is None or unix_time == "":
        return ""
    try:
        if isinstance(unix_time, str):
            unix_time = float(unix_time)
        # 13桁以上はミリ秒とみなす
        if unix_time > 9999999999:
            unix_time = unix_time / 1000
        dt = datetime.datetime.fromtimestamp(unix_time)
        return dt.strftime('%Y/%m/%d %H:%M:%S')
    except (ValueError, TypeError, OSError):
        return ""

def main(**kwargs):
    return get_events.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !*WMC URL!        # type: ignore
    TOKEN = !*アクセストークン!    # type: ignore
    INDEX = !*インデックス!        # 0始まり。負数も可。 # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not INDEX or not str(INDEX).strip():
        missing_params.append("インデックス")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

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

    # 配列条件（カンマ区切り）
    LEVELS = !重要度(0~3)!          # 例: "0,1,3"  # type: ignore
    LABELS = !イベントラベル!        # type: ignore
    WACT_IDS = !検索WinActorID!      # type: ignore

    # メッセージ条件
    MESSAGE_TYPE = !メッセージ検索条件|完全一致,部分一致,AND/NOT検索!  # type: ignore
    if MESSAGE_TYPE == "完全一致":
        MESSAGE_TYPE = "perfect"
    elif MESSAGE_TYPE == "部分一致":
        MESSAGE_TYPE = "partial"
    elif MESSAGE_TYPE == "AND/NOT検索":
        MESSAGE_TYPE = "andnot"

    MESSAGE = !メッセージ!  # type: ignore

    # ソート・ページング
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

        # 配列系（get_events.run 側で list 化されるため、ここでは文字列のままでもOK）
        "level[]": _norm(LEVELS),
        "label[]": _norm(LABELS),
        "winactorId[]": _norm(WACT_IDS),

        "messageType": _norm(MESSAGE_TYPE),
        "message": _norm(MESSAGE),
        "sort": _norm(SORT),
        "sortDirection": _norm(SORT_DIR),
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

    # 空値を除去
    params = {k: v for k, v in raw_params.items() if v not in (None, "", [])}

    # 実行（params はトップレベル kwargs として渡す）
    result = main(base_url=BASE_URL, token=TOKEN, **params)

    # イベント情報（指定INDEX）の全項目を取得
    # 大きなインデックスに対応するため、base_url, token, 検索条件を渡す
    event = get_events.get_event_info(
        result, 
        INDEX, 
        base_url=BASE_URL, 
        token=TOKEN, 
        **params  # 検索条件も渡す
    )

    # 取得結果を WinActor 変数に格納
    winactor.set_variable($重要度$, event["level"])                       # type: ignore
    winactor.set_variable($イベントラベル$, event["label"])               # type: ignore
    winactor.set_variable($WinActorID$, event["winactorId"])             # type: ignore
    winactor.set_variable($ファイルID$, event["fileId"])                 # type: ignore
    winactor.set_variable($シナリオID$, event["scenarioId"])             # type: ignore
    winactor.set_variable($スケジュールID$, event["scheduleId"])         # type: ignore
    winactor.set_variable($タスクID$, event["taskId"])                   # type: ignore
    winactor.set_variable($ユーザID$, event["userId"])                   # type: ignore
    winactor.set_variable($所属ID$, event["departmentId"])               # type: ignore
    winactor.set_variable($ロールID$, event["roleId"])                   # type: ignore
    winactor.set_variable($ステージID$, event["stageId"])                 # type: ignore
    winactor.set_variable($個別ステージID$, event["particularStageId"])   # type: ignore
    winactor.set_variable($その他$, event["other"])                       # type: ignore
    winactor.set_variable($メッセージ$, event["message"])                 # type: ignore
    winactor.set_variable($実施主体$, event["subject"])                   # type: ignore
    winactor.set_variable($実施主体所属$, event["subjectDepartment"])     # type: ignore
    winactor.set_variable($実施主体ロール$, event["subjectRole"])         # type: ignore
    winactor.set_variable($作成時刻$, unix_to_datetime(event["createdTime"]))         # type: ignore
    winactor.set_variable($所属名$, event["departmentName"])             # type: ignore
    winactor.set_variable($実施主体所属名$, event["subjectDepartmentName"]) # type: ignore
