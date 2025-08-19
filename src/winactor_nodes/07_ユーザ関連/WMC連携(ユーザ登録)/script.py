import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.users import post_users

# 各種パラメータ
BASE_URL = !WMC URL!  # type: ignore
TOKEN = !アクセストークン!  # type: ignore
NAME = !ユーザ名!  # type: ignore
PASSWORD = !パスワード!  # type: ignore
ROLE = !ロール!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
AUTO_LOGOUT = !オートログアウト(秒)!  # type: ignore
EMAIL = !通知先メールアドレス!  # type: ignore
APPROVAL = !承認通知|無効,有効!  # type: ignore
TASK = !タスク異常通知|無効,有効!  # type: ignore
WINACTOR = !WinActor異常通知|無効,有効!  # type: ignore
WINACTOR_LIMIT = !WinActor接続数上限通知|無効,有効!  # type: ignore
UNDEFINED_WINACTOR = !未所属WinActor接続通知|無効,有効!  # type: ignore
WINACTOR_LICENSE = !WinActorライセンス期限通知|無効,有効!  # type: ignore
TRAFFIC = !通信量超過通知|無効,有効!  # type: ignore
STORAGE = !ストレージ使用量超過通知|無効,有効!  # type: ignore
REMAINING_LICENSE = !ライセンス数上限通知|無効,有効!  # type: ignore
WINACTOR_ID = !WinActorID!  # type: ignore


def main(**kwargs):
    return post_users.run(**kwargs)


if __name__ == "__main__":

    # "無効"/"有効" -> "false"/"true" に再代入
    if APPROVAL == "無効":
        APPROVAL = "false"
    elif APPROVAL == "有効":
        APPROVAL = "true"

    if TASK == "無効":
        TASK = "false"
    elif TASK == "有効":
        TASK = "true"

    if WINACTOR == "無効":
        WINACTOR = "false"
    elif WINACTOR == "有効":
        WINACTOR = "true"

    if WINACTOR_LIMIT == "無効":
        WINACTOR_LIMIT = "false"
    elif WINACTOR_LIMIT == "有効":
        WINACTOR_LIMIT = "true"

    if UNDEFINED_WINACTOR == "無効":
        UNDEFINED_WINACTOR = "false"
    elif UNDEFINED_WINACTOR == "有効":
        UNDEFINED_WINACTOR = "true"

    if WINACTOR_LICENSE == "無効":
        WINACTOR_LICENSE = "false"
    elif WINACTOR_LICENSE == "有効":
        WINACTOR_LICENSE = "true"

    if TRAFFIC == "無効":
        TRAFFIC = "false"
    elif TRAFFIC == "有効":
        TRAFFIC = "true"

    if STORAGE == "無効":
        STORAGE = "false"
    elif STORAGE == "有効":
        STORAGE = "true"

    if REMAINING_LICENSE == "無効":
        REMAINING_LICENSE = "false"
    elif REMAINING_LICENSE == "有効":
        REMAINING_LICENSE = "true"

    user_data = {}

    if NAME:
        _name = str(NAME).strip()
        if _name:
            user_data["name"] = _name
    if PASSWORD:
        user_data["password"] = str(PASSWORD).strip()

    if ROLE:
        _role = str(ROLE).strip()
        if _role:
            user_data["role"] = _role

    if DESCRIPTION:
        user_data["description"] = DESCRIPTION
    if AUTO_LOGOUT:
        user_data["autoLogout"] = int(AUTO_LOGOUT)
    if EMAIL:
        _email = str(EMAIL).strip()
        if _email:
            user_data["email"] = _email

    # "true"/"false" -> True/False に設定
    if APPROVAL == "true":
        user_data["notifyApproval"] = True
    elif APPROVAL == "false":
        user_data["notifyApproval"] = False

    if TASK == "true":
        user_data["notifyTask"] = True
    elif TASK == "false":
        user_data["notifyTask"] = False

    if WINACTOR == "true":
        user_data["notifyWinactor"] = True
    elif WINACTOR == "false":
        user_data["notifyWinactor"] = False

    if WINACTOR_LIMIT == "true":
        user_data["notifyWinactorLimit"] = True
    elif WINACTOR_LIMIT == "false":
        user_data["notifyWinactorLimit"] = False

    if UNDEFINED_WINACTOR == "true":
        user_data["notifyUndefinedWinactor"] = True
    elif UNDEFINED_WINACTOR == "false":
        user_data["notifyUndefinedWinactor"] = False

    if WINACTOR_LICENSE == "true":
        user_data["notifyWinactorLicense"] = True
    elif WINACTOR_LICENSE == "false":
        user_data["notifyWinactorLicense"] = False

    if TRAFFIC == "true":
        user_data["notifyTraffic"] = True
    elif TRAFFIC == "false":
        user_data["notifyTraffic"] = False

    if STORAGE == "true":
        user_data["notifyStorage"] = True
    elif STORAGE == "false":
        user_data["notifyStorage"] = False

    if REMAINING_LICENSE == "true":
        user_data["notifyRemainingLicense"] = True
    elif REMAINING_LICENSE == "false":
        user_data["notifyRemainingLicense"] = False

    if WINACTOR_ID:
        _winactorid = str(WINACTOR_ID).strip()
        if _winactorid:
            user_data["winactorId"] = _winactorid

    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        user_data=user_data,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )

    user_id = result.get("id", "")  # idが無い場合は空文字
    winactor.set_variable($ユーザID$, user_id)  # type: ignore