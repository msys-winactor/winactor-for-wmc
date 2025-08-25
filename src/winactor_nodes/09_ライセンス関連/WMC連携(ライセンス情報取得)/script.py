# main.py
import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.licenses import get_licenses


def main(**kwargs):
    return get_licenses.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!      # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    INDEX = !インデックス!      # 0始まり。負数も可。 # type: ignore

    # Feature配列のインデックス（必要な場合のみ使用。0始まり。負数可）
    FEATURE_INDEX = !Featureインデックス!  # type: ignore

    # 必要に応じて指定（未入力は無視されます）
    WINACTOR_NAME_TYPE = !WinActor名検索条件|perfect,partial!              # type: ignore
    WINACTOR_NAME = !WinActor名!                                            # type: ignore
    PC_NAME_TYPE = !PC名検索条件|perfect,partial!                           # type: ignore
    PC_NAME = !PC名!                                                        # type: ignore
    USER_NAME_TYPE = !ユーザ名検索条件|perfect,partial!                     # type: ignore
    USER_NAME = !ユーザ名!                                                  # type: ignore
    LICENSE_GROUP_NAME_TYPE = !ライセンスグループ名検索条件|perfect,partial!  # type: ignore
    LICENSE_GROUP_NAME = !ライセンスグループ名!                              # type: ignore
    SORT = !ソート項目|pcName,userName,licenseGroupName!                    # type: ignore
    SORT_DIRECTION = !ソート順|asc,desc!                                    # type: ignore

    # クエリパラメータ（空文字やNoneは除外）
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

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        **params
    )

    # ライセンス情報（指定INDEX）の全項目を取得
    license_info = get_licenses.get_license_info(result, INDEX)
    # Feature情報（指定FEATURE_INDEX）の全項目を取得（必要な場合）
    feature_info = get_licenses.get_feature_info(result, FEATURE_INDEX)

    # ライセンス情報を WinActor 変数に格納（数値は数値のまま）
    winactor.set_variable($ライセンスID$, license_info["id"])                 # type: ignore
    winactor.set_variable($ユーザ名$, license_info["userName"])                # type: ignore
    winactor.set_variable($PC名$, license_info["pcName"])                     # type: ignore
    winactor.set_variable($ライセンス無効化までの期限$, license_info["expiration"])  # type: ignore
    winactor.set_variable($ロケール$, license_info["locale"])                 # type: ignore
    winactor.set_variable($Feature名$, license_info["featureName"])           # type: ignore
    winactor.set_variable($WinActor名$, license_info["winactorName"])         # type: ignore
    winactor.set_variable($ライセンスグループ名$, license_info["licenseGroupName"])  # type: ignore

    # Feature情報を WinActor 変数に格納（不要ならこのブロックは削除）
    winactor.set_variable($Feature名称$, feature_info["name"])                # type: ignore
    winactor.set_variable($ライセンス種別$, feature_info["licenseType"])       # type: ignore
    winactor.set_variable($ライセンス有効期限$, feature_info["deathTime"])      # type: ignore
    winactor.set_variable($ライセンス開始日時$, feature_info["startTime"])      # type: ignore
    winactor.set_variable($ライセンス数$, feature_info["numLicenses"])         # type: ignore
    winactor.set_variable($評価期間残日数$, feature_info["trialDaysLeft"])      # type: ignore
    winactor.set_variable($Feature通信インターバル$, feature_info["keyLifeTime"])  # type: ignore
    winactor.set_variable($ライセンスロケール$, feature_info["locale"])         # type: ignore