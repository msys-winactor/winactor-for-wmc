from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")

    if not base_url or not token:
        return {}

    allowed = (
        "winactorNameType",
        "winactorName",
        "pcNameType",
        "pcName",
        "userNameType",
        "userName",
        "licenseGroupNameType",
        "licenseGroupName",
        "sort",
        "sortDirection",
    )
    params = {k: kwargs[k] for k in kwargs.keys() & set(allowed)}

    endpoint = "/licenses"
    client = WMCApiClient(base_url, token)
    response = client.get(endpoint, params=params)
    return response


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


def get_license_info(result, index=0):
    """
    ライセンス一覧APIのレスポンスから指定インデックスのライセンス情報を返す。
    次の場合は例外を送出:
      - index 未指定/空欄
      - index が数値化不可
      - レスポンスが不正（dictでない、または licenses が存在しない/空）
      - index 範囲外
    """
    _ensure_index_provided(index, "ライセンスのインデックス")

    if not isinstance(result, dict):
        raise ValueError("APIレスポンスが不正です（dict ではありません）。")

    licenses = result.get("licenses")
    if not isinstance(licenses, list) or len(licenses) == 0:
        raise ValueError("ライセンス情報が存在しません。")

    try:
        idx = int(index)
    except (TypeError, ValueError):
        raise ValueError("ライセンスのインデックスが数値ではありません。")

    if idx < -len(licenses) or idx >= len(licenses):
        raise ValueError("ライセンスのインデックスが範囲外です。")

    target = licenses[idx] or {}
    return {
        "id": target.get("id", "") or "",
        "userName": target.get("userName", "") or "",
        "pcName": target.get("pcName", "") or "",
        "expiration": _safe_int(target.get("expiration", 0), 0),
        "locale": target.get("locale", "") or "",
        "featureName": target.get("featureName", "") or "",
        "winactorName": target.get("winactorName", "") or "",
        "licenseGroupName": target.get("licenseGroupName", "") or "",
    }
