import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.scenarios import post_scenarios

# 各種パラメータ
BASE_URL = !*WMC URL!  # type: ignore
TOKEN = !*アクセストークン!  # type: ignore
FILE_ID = !*ファイルID!  # type: ignore
NAME = !*名前!  # type: ignore
PASSWORD = !パスワード!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
TIMEOUT = !タイムアウト!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
FUNCTION_TAG = !機能タグ!  # type: ignore
SCENARIO_TAG = !シナリオタグ!  # type: ignore
SIMPLE_MODE = !シンプルモード|無効,有効!  # type: ignore

def main(**kwargs):
    return post_scenarios.run(**kwargs)

if __name__ == "__main__":

    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not NAME or not str(NAME).strip():
        missing_params.append("名前")
    if not FILE_ID or not str(FILE_ID).strip():
        missing_params.append("ファイルID")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # SIMPLE_MODE 再代入
    if SIMPLE_MODE == "無効":
        SIMPLE_MODE = "false"
    elif SIMPLE_MODE == "有効":
        SIMPLE_MODE = "true"

    scenario_data = {}

    if FILE_ID:
        scenario_data["fileId"] = FILE_ID
    if NAME:
        _name = NAME.strip()
        if _name:
            scenario_data["name"] = _name
    if PASSWORD:
        scenario_data["password"] = PASSWORD
    if TIMEOUT:
        scenario_data["timeout"] = int(TIMEOUT)
    if DESCRIPTION:
        scenario_data["description"] = DESCRIPTION
    if FUNCTION_TAG:
        scenario_data["functionTag"] = FUNCTION_TAG
    if SCENARIO_TAG:
        scenario_data["scenarioTag"] = SCENARIO_TAG
    if SIMPLE_MODE == "true":
        scenario_data["simpleMode"] = True
    elif SIMPLE_MODE == "false":
        scenario_data["simpleMode"] = False

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        scenario_data=scenario_data,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )
    scenario_id = result.get('id', '')  # idが無い場合は空文字
    winactor.set_variable($シナリオID$, scenario_id)  # type: ignore
