from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    """
    /events を呼び出し、レスポンス(JSON)をそのまま返す。
    総件数の取り出しは get_number() を使用する。
    受け取り(例):
      - base_url: API ベースURL (必須)
      - token: アクセストークン (必須)
      - params: dict 形式のクエリパラメータ（任意）
      - もしくはクエリ項目をトップレベル kwargs として渡してもよい
      - departments_url, department_name1..3 を指定した場合は部門名からIDへ変換して department1..3 を補完
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

    # 部門名 → ID 変換（ID 未指定時のみ補完）
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

    # リスト系のキーは list 化（カンマ区切りにも対応）
    for key in ("level[]", "label[]", "winactorId[]"):
        if key in params:
            params[key] = _ensure_list(params[key])

    endpoint = "/events"
    client = WMCApiClient(base_url, token)
    return client.get(endpoint, params=params)


def get_number(result):
    """
    /events のレスポンスから total（総件数）を返す。
    - レスポンスが不正、または total が取得できない場合は 0 を返す。
    """
    if not isinstance(result, dict):
        return 0
    total = result.get("total", 0)
    return _safe_int(total, 0)


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
