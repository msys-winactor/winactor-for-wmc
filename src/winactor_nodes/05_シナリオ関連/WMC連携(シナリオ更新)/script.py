# main_update_scenario.py

import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.scenarios import put_scenarios

# 各種パラメータ（POST版と同じ定義）
BASE_URL = !WMC URL!  # type: ignore
TOKEN = !アクセストークン!  # type: ignore
SCENARIO_ID = !シナリオID!  # type: ignore
FILE_ID = !ファイルID!  # type: ignore
NAME = !名前!  # type: ignore
PASSWORD = !パスワード!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
TIMEOUT = !タイムアウト!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
FUNCTION_TAG = !機能タグ!  # type: ignore
SCENARIO_TAG = !シナリオタグ!  # type: ignore
SIMPLE_MODE = !シンプルモード|無効,有効!  # type: ignore
MESSAGES = !修正内容!  # type: ignore  # 自由入力

def main(**kwargs):
    return put_scenarios.run(**kwargs)

if __name__ == "__main__":
    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not SCENARIO_ID or not str(SCENARIO_ID).strip():
        missing_params.append("シナリオID")
    if not NAME or not str(NAME).strip():
        missing_params.append("名前")
    if not FILE_ID or not str(FILE_ID).strip():
        missing_params.append("ファイルID")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # SIMPLE_MODE 再代入（文字列→真偽値文字列）
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
    # パスワードは指定時のみ更新フラグを立てる
    if PASSWORD:
        scenario_data["updatePassword"] = True
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


    if MESSAGES is not None:
        _messages = str(MESSAGES).strip()
        if _messages:
            scenario_data["messages"] = _messages

    # overwrite は常に True
    scenario_data["overwrite"] = True


    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        scenario_id=SCENARIO_ID,
        scenario_data=scenario_data,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )
    # updated_scenario_id の変数更新（WinActor変数への書き戻し）は行いません
