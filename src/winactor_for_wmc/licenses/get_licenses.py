# winactor_for_wmc/licenses/get_licenses.py
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")

    if not base_url or not token:
        return {}

    # スクリプト側で整形済みのクエリパラメータをそのまま使う
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


def get_license_info(result, index=0):
    """
    ライセンス一覧APIのレスポンスから指定インデックスの
    全ライセンス情報を dict で返す。
    - index: 0始まり。負のインデックス可（Python準拠）
    - 不正値や範囲外、データなしの場合は空値/0で構成したdictを返す
    """
    empty = {
        "id": "",
        "userName": "",
        "pcName": "",
        "expiration": 0,
        "locale": "",
        "featureName": "",
        "winactorName": "",
        "licenseGroupName": "",
    }

    licenses = result.get("licenses", []) if isinstance(result, dict) else []
    try:
        idx = int(index)
    except (TypeError, ValueError):
        return empty

    if not licenses:
        return empty
    if idx < -len(licenses) or idx >= len(licenses):
        return empty

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


def get_feature_info(result, index=0):
    """
    ライセンス一覧APIのレスポンスから指定インデックスの
    Feature情報を dict で返す。
    - index: 0始まり。負のインデックス可（Python準拠）
    - 不正値や範囲外、データなしの場合は空値/0で構成したdictを返す
    """
    empty = {
        "name": "",
        "licenseType": 0,
        "deathTime": 0,
        "startTime": 0,
        "numLicenses": 0,
        "trialDaysLeft": 0,
        "keyLifeTime": 0,
        "locale": "",
    }

    features = result.get("features", []) if isinstance(result, dict) else []
    try:
        idx = int(index)
    except (TypeError, ValueError):
        return empty

    if not features:
        return empty
    if idx < -len(features) or idx >= len(features):
        return empty

    target = features[idx] or {}
    return {
        "name": target.get("name", "") or "",
        "licenseType": _safe_int(target.get("licenseType", 0), 0),
        "deathTime": _safe_int(target.get("deathTime", 0), 0),
        "startTime": _safe_int(target.get("startTime", 0), 0),
        "numLicenses": _safe_int(target.get("numLicenses", 0), 0),
        "trialDaysLeft": _safe_int(target.get("trialDaysLeft", 0), 0),
        "keyLifeTime": _safe_int(target.get("keyLifeTime", 0), 0),
        "locale": target.get("locale", "") or "",
    }
