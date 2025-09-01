from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    """
    /events を呼び出してイベント一覧を取得する。

    受け取り(例):
      - base_url: API ベースURL (必須)
      - token: アクセストークン (必須)
      - params: dict 形式のクエリパラメータ（任意）
      - もしくはクエリ項目をトップレベル kwargs として渡してもよい
      - departments_url, department_name1..3 を指定した場合は部門名からIDへ変換して department1..3 を補完
    返り値:
      - API の JSON レスポンス(dict)。base_url/token 不足時は {} を返す。
    """
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    if not base_url or not token:
        return {}

    # params（dict）で渡されたものと、トップレベル kwargs の両方に対応
    raw_params = dict(kwargs.get("params") or {})
    for k, v in kwargs.items():
        if k not in ("base_url", "token", "params"):
            raw_params.setdefault(k, v)

    # 部門名 → ID 変換（ID未指定時のみ補完）
    departments_url = raw_params.get("departments_url") or base_url
    dn1 = raw_params.get("department_name1")
    dn2 = raw_params.get("department_name2")
    dn3 = raw_params.get("department_name3")
    if (dn1 or dn2 or dn3) and not (
        raw_params.get("department1")
        or raw_params.get("department2")
        or raw_params.get("department3")
    ):
        try:
            dep_result = get_departments.get_departments(
                base_url=departments_url, token=token
            )
            d1_id, d2_id, d3_id = get_departments.get_departments_ids_by_names(
                dep_result,
                department_name1=dn1,
                department_name2=dn2,
                department_name3=dn3,
            )
            if d1_id is not None:
                raw_params["department1"] = d1_id
            if d2_id is not None:
                raw_params["department2"] = d2_id
            if d3_id is not None:
                raw_params["department3"] = d3_id
        except Exception:
            # 取得や変換に失敗しても処理は続行（部門条件なしで検索）
            pass

    # 許可されたパラメータのみ抽出
    allowed = (
        "department1",
        "department2",
        "department3",
        "createdAtType",
        "createdAtDate1",
        "createdAtTime1",
        "createdAtDate2",
        "createdAtTime2",
        "level[]",
        "label[]",
        "winactorId[]",
        "messageType",
        "message",
        "sort",
        "sortDirection",
        "page",
        "size",
    )
    params = {k: raw_params[k] for k in raw_params.keys() & set(allowed)}

    # リスト系のキーは list 化しておく（呼び出し側がカンマ区切り文字列等を渡す場合にも対応）
    for key in ("level[]", "label[]", "winactorId[]"):
        if key in params:
            params[key] = _ensure_list(params[key])

    endpoint = "/events"
    client = WMCApiClient(base_url, token)
    return client.get(endpoint, params=params)


def _ensure_list(value):
    """
    値をリスト化するヘルパ。
    - すでに list/tuple/set の場合は list 化
    - カンマ区切りの str は分割
    - それ以外は単一要素リストに包む
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        if value.strip() == "":
            return []
        return [v.strip() for v in value.split(",")]
    return [value]


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _ensure_index_provided(index, name):
    if index is None:
        raise ValueError(f"{name} が未指定です。")
    if isinstance(index, str) and index.strip() == "":
        raise ValueError(f"{name} が未指定です。")


def get_event_info(result, index=0):
    """
    イベント一覧APIのレスポンスから指定インデックスのイベント情報を返す。
    例外発生条件:
      - index 未指定/空欄
      - index が数値化不可
      - レスポンスが不正（dictでない、または items が存在しない/空）
      - index 範囲外
    返却フィールド（存在しないものは既定値）:
      - level(int), label(int), winactorId(str), fileId(str), scenarioId(str),
        scheduleId(str), taskId(str), userId(str), departmentId(str), roleId(str),
        stageId(str), particularStageId(str), other(str), message(str),
        subject(str), subjectDepartment(str), subjectRole(str),
        createdTime(int), departmentName(str), subjectDepartmentName(str)
    """
    _ensure_index_provided(index, "イベントのインデックス")

    if not isinstance(result, dict):
        raise ValueError("APIレスポンスが不正です（dict ではありません）。")

    items = result.get("items")
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("イベント情報が存在しません。")

    try:
        idx = int(index)
    except (TypeError, ValueError):
        raise ValueError("イベントのインデックスが数値ではありません。")

    if idx < -len(items) or idx >= len(items):
        raise ValueError("イベントのインデックスが範囲外です。")

    target = items[idx] or {}

    return {
        "level": _safe_int(target.get("level", 0), 0),
        "label": _safe_int(target.get("label", 0), 0),
        "winactorId": target.get("winactorId", "") or "",
        "fileId": target.get("fileId", "") or "",
        "scenarioId": target.get("scenarioId", "") or "",
        "scheduleId": target.get("scheduleId", "") or "",
        "taskId": target.get("taskId", "") or "",
        "userId": target.get("userId", "") or "",
        "departmentId": target.get("departmentId", "") or "",
        "roleId": target.get("roleId", "") or "",
        "stageId": target.get("stageId", "") or "",
        "particularStageId": target.get("particularStageId", "") or "",
        "other": target.get("other", "") or "",
        "message": target.get("message", "") or "",
        "subject": target.get("subject", "") or "",
        "subjectDepartment": target.get("subjectDepartment", "") or "",
        "subjectRole": target.get("subjectRole", "") or "",
        "createdTime": _safe_int(target.get("createdTime", 0), 0),
        "departmentName": target.get("departmentName", "") or "",
        "subjectDepartmentName": target.get("subjectDepartmentName", "") or "",
    }
