import sys
import datetime

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.licenses import get_licenses_usagestatus


def unix_to_datetime(unix_time):
    """
    UNIXタイムをyyyy/mm/dd hh:mm:ss形式に変換
 
    Args:
        unix_time (int or float): UNIXタイムスタンプ（秒またはミリ秒）
 
    Returns:
        str: yyyy/mm/dd hh:mm:ss形式の文字列
    """
    if unix_time is None or unix_time == "":
        return ""
    
    try:
        # 文字列の場合は数値に変換
        if isinstance(unix_time, str):
            unix_time = float(unix_time)
        
        # ミリ秒単位かどうかを判定（13桁以上の場合はミリ秒とみなす）
        if unix_time > 9999999999:  # 10桁を超える場合（2001年以降の日付でミリ秒単位）
            unix_time = unix_time / 1000
        
        dt = datetime.datetime.fromtimestamp(unix_time)
        return dt.strftime('%Y/%m/%d %H:%M:%S')
    
    except (ValueError, TypeError, OSError) as e:
        return ""


def main(**kwargs):
    return get_licenses_usagestatus.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !*WMC URL!      # type: ignore
    TOKEN = !*アクセストークン!  # type: ignore
    INDEX = !*インデックス!      # 0始まり。負数も可。 # type: ignore

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

    # 必要に応じて指定（未入力は無視）
    WINACTOR_NAME_TYPE = !WinActor名検索条件|完全一致,部分一致!              # type: ignore
    WINACTOR_NAME = !WinActor名!                                            # type: ignore
    PC_NAME_TYPE = !PC名検索条件|完全一致,部分一致!                           # type: ignore
    PC_NAME = !PC名!                                                        # type: ignore
    USER_NAME_TYPE = !ユーザ名検索条件|完全一致,部分一致!                     # type: ignore
    USER_NAME = !ユーザ名!                                                  # type: ignore
    LICENSE_GROUP_NAME_TYPE = !ライセンスグループ名検索条件|完全一致,部分一致!  # type: ignore
    LICENSE_GROUP_NAME = !ライセンスグループ名!                              # type: ignore
    SORT = !ソート項目|ライセンスグループ名,PC名,ユーザ名!                    # type: ignore
    SORT_DIRECTION = !ソート順|昇順,降順!                                    # type: ignore

    #再代入
    if WINACTOR_NAME_TYPE == "完全一致":
        WINACTOR_NAME_TYPE = "perfect"
    elif WINACTOR_NAME_TYPE == "部分一致":
        WINACTOR_NAME_TYPE = "partial"

    if PC_NAME_TYPE == "完全一致":
        PC_NAME_TYPE = "perfect"
    elif PC_NAME_TYPE == "部分一致":
        PC_NAME_TYPE = "partial"

    if USER_NAME_TYPE == "完全一致":
        USER_NAME_TYPE = "perfect"
    elif USER_NAME_TYPE == "部分一致":
        USER_NAME_TYPE = "partial"

    if LICENSE_GROUP_NAME_TYPE == "完全一致":
        LICENSE_GROUP_NAME_TYPE = "perfect"
    elif LICENSE_GROUP_NAME_TYPE == "部分一致":
        LICENSE_GROUP_NAME_TYPE = "partial"

    if SORT == "PC名":
        SORT = "pcName"
    elif SORT == "ユーザ名":
        SORT = "userName"
    elif SORT == "ライセンスグループ名":
        SORT = "licenseGroupName"

    if SORT_DIRECTION == "昇順":
        SORT_DIRECTION = "asc"
    elif SORT_DIRECTION == "降順":
        SORT_DIRECTION = "desc"

    raw_params = {
        "winactorNameType": WINACTOR_NAME_TYPE,
        "winactorName": WINACTOR_NAME,
        "pcNameType": PC_NAME_TYPE,
        "pcName": PC_NAME,
        "userNameType": USER_NAME_TYPE,
        "userName": USER_NAME,
        "licenseGroupNameType": LICENSE_GROUP_NAME_TYPE,
        "licenseGroupName": LICENSE_GROUP_NAME,
        "sort": SORT,
        "sortDirection": SORT_DIRECTION,
    }
    params = {}
    for k, v in raw_params.items():
        if isinstance(v, str):
            v = v.strip()
        if v not in (None, ""):
            params[k] = v

    result = main(base_url=BASE_URL, token=TOKEN, **params)

    # ライセンス情報（指定INDEX）の全項目を取得（未指定/不正/範囲外はモジュール側で例外）
    license_info = get_licenses_usagestatus.get_license_info(result, INDEX)

    # ライセンス情報を WinActor 変数に格納（数値は数値のまま）
    winactor.set_variable($ライセンスID$, license_info["id"])                  # type: ignore
    winactor.set_variable($ユーザ名$, license_info["userName"])                 # type: ignore
    winactor.set_variable($PC名$, license_info["pcName"])                      # type: ignore
    winactor.set_variable($ライセンス無効化までの期限$, unix_to_datetime(license_info["expiration"]))   # type: ignore
    winactor.set_variable($ロケール$, license_info["locale"])                  # type: ignore
    winactor.set_variable($Feature名称$, license_info["featureName"])            # type: ignore
    winactor.set_variable($WinActor名$, license_info["winactorName"])          # type: ignore
    winactor.set_variable($ライセンスグループ名$, license_info["licenseGroupName"])   # type: ignore
