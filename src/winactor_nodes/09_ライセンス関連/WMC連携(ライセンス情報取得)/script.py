# main_features_minimal.py
import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.licenses import get_licenses


def main(**kwargs):
    return get_licenses.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!        # type: ignore
    TOKEN = !アクセストークン!    # type: ignore
    FEATURE_INDEX = !ライセンス名|フル機能版,実行版,管理実行版!   # type: ignore

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
    winactor.set_variable($ライセンス有効期限$, feature_info["deathTime"])       # type: ignore
    winactor.set_variable($ライセンス開始日時$, feature_info["startTime"])       # type: ignore
    winactor.set_variable($ライセンス数$, feature_info["numLicenses"])          # type: ignore
    winactor.set_variable($評価期間残日数$, feature_info["trialDaysLeft"])       # type: ignore
    winactor.set_variable($通信インターバル$, feature_info["keyLifeTime"])   # type: ignore
    winactor.set_variable($ライセンスロケール$, feature_info["locale"])           # type: ignore