import sys
import datetime

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.licenses import get_licenses

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
    return get_licenses.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !*WMC URL!        # type: ignore
    TOKEN = !*アクセストークン!    # type: ignore
    FEATURE_INDEX = !ライセンス名|フル機能版,実行版,管理実行版!   # type: ignore

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    #再代入
    if FEATURE_INDEX == "フル機能版":
        FEATURE_INDEX = 0
    elif FEATURE_INDEX == "実行版":
        FEATURE_INDEX = 1
    elif FEATURE_INDEX == "管理実行版":
        FEATURE_INDEX = 2

    # API呼び出し（クエリ条件やソートは一切送らない）
    result = main(base_url=BASE_URL, token=TOKEN)

    # Feature情報（指定FEATURE_INDEX）の全項目を取得（未指定/不正/範囲外はモジュール側で例外）
    feature_info = get_licenses.get_feature_info(result, FEATURE_INDEX)

    # Feature情報を WinActor 変数に格納（数値は数値のまま）
    winactor.set_variable($ライセンス名称$, feature_info["name"])                 # type: ignore
    winactor.set_variable($ライセンス種別$, feature_info["licenseType"])        # type: ignore
    winactor.set_variable($ライセンス有効期限$, unix_to_datetime(feature_info["deathTime"]))       # type: ignore
    winactor.set_variable($ライセンス開始日時$, unix_to_datetime(feature_info["startTime"]))       # type: ignore
    winactor.set_variable($ライセンス数$, feature_info["numLicenses"])          # type: ignore
    winactor.set_variable($評価期間残日数$, feature_info["trialDaysLeft"])       # type: ignore
    winactor.set_variable($通信インターバル$, feature_info["keyLifeTime"])   # type: ignore
    winactor.set_variable($ライセンスロケール$, feature_info["locale"])           # type: ignore
