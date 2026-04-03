import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.winactors import put_winactors

# 各種パラメータ
BASE_URL = !*WMC URL!  # type: ignore
TOKEN = !*アクセストークン!  # type: ignore
WINACTOR_ID = !*WinActorID!  # type: ignore
NAME = !*WinActor名!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
FUNCTIONTAG = !機能タグ!  # type: ignore
AUTOREBOOT = !自動再起動|しない,する!  # type: ignore
KIND = !自動再起動種別|毎日,毎週!  # type: ignore
DAYOFWEEK = !曜日|月曜日,火曜日,水曜日,木曜日,金曜日,土曜日,日曜日!  # type: ignore
REBOOTTIME = !再起動時刻(hh:mm:ss)!  # type: ignore

def main(**kwargs):
    return put_winactors.run(**kwargs)

if __name__ == "__main__":
    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not WINACTOR_ID or not str(WINACTOR_ID).strip():
        missing_params.append("WinActorID")
    if not NAME or not str(NAME).strip():
        missing_params.append("WinActor名")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # AUTOREBOOT 再代入（bool化）
    auto_map = {
        "する": "true",
        "しない": "false",
    }
    AUTOREBOOT = auto_map.get(AUTOREBOOT.strip(), "") if AUTOREBOOT else ""
    auto_reboot_bool = AUTOREBOOT.strip().lower() == "true" if AUTOREBOOT else False

    # KIND 再代入
    kind_map = {
        "毎日": "daily",
        "毎週": "weekly",
    }
    KIND = kind_map.get(KIND.strip(), "") if KIND else ""

    # DAYOFWEEK 再代入
    dayofweek_map = {
        "日曜日": "sunday",
        "月曜日": "monday",
        "火曜日": "tuesday",
        "水曜日": "wednesday",
        "木曜日": "thursday",
        "金曜日": "friday",
        "土曜日": "saturday",
    }
    DAYOFWEEK = dayofweek_map.get(DAYOFWEEK.strip(), "") if DAYOFWEEK else ""

    # WinActor更新用作成
    winactor_dict = {}

    if NAME:
        winactor_dict["name"] = NAME.strip()
    if DESCRIPTION:
        winactor_dict["description"] = DESCRIPTION.strip()
    if FUNCTIONTAG:
        winactor_dict["functionTag"] = FUNCTIONTAG.strip()

    # 自動再起動関連
    winactor_dict["autoReboot"] = auto_reboot_bool
    if auto_reboot_bool:
        if KIND:
            winactor_dict["kind"] = KIND.strip()
        if KIND == "weekly" and DAYOFWEEK:
            winactor_dict["dayOfWeek"] = DAYOFWEEK.strip()
        if REBOOTTIME:
            winactor_dict["rebootTime"] = REBOOTTIME.strip()

    # main呼び出し
    result = main(
        winactors_url=BASE_URL,
        departments_url=BASE_URL,
        token=TOKEN,
        winactor_id=WINACTOR_ID,
        winactor_data=winactor_dict,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )
