import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.users import get_users

def main(**kwargs):
    return get_users.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!      # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    USER_NAME = !ユーザ名!     # type: ignore

    # ユーザ名だけ渡せばOK
    result = main(base_url=BASE_URL, token=TOKEN, user_name=USER_NAME)

    if isinstance(result, dict):
        winactor.set_variable($ユーザID$, result.get("id", ""))                              # type: ignore
        winactor.set_variable($ユーザ名$, result.get("name", ""))                            # type: ignore
        winactor.set_variable($親所属ID$, result.get("department1", 0))                     # type: ignore
        winactor.set_variable($子所属ID$, result.get("department2", 0))                     # type: ignore
        winactor.set_variable($孫所属ID$, result.get("department3", 0))                     # type: ignore
        winactor.set_variable($所属名$, result.get("departmentName", ""))                   # type: ignore
        winactor.set_variable($ステータス$, result.get("status", ""))                        # type: ignore
        winactor.set_variable($権限名$, result.get("role", ""))                             # type: ignore
        winactor.set_variable($説明$, result.get("description", ""))                        # type: ignore
        winactor.set_variable($オートログアウト$, result.get("autoLogout", 0))               # type: ignore
        winactor.set_variable($役職$, result.get("position", ""))                           # type: ignore
        winactor.set_variable($連続ログイン失敗回数$, result.get("loginFailureCount", 0))     # type: ignore
        winactor.set_variable($最終ログイン失敗日時$, result.get("loginFailureDate", 0))     # type: ignore
        winactor.set_variable($最終ログイン日時$, result.get("lastLoginDate", 0))            # type: ignore
        winactor.set_variable($作成日時$, result.get("createdTime", 0))                      # type: ignore
        winactor.set_variable($作成者ユーザID$, result.get("creatorId", ""))                # type: ignore
        winactor.set_variable($更新日時$, result.get("updatedTime", 0))                      # type: ignore
        winactor.set_variable($メールアドレス$, result.get("email", ""))                     # type: ignore
        winactor.set_variable($承認通知有無$, result.get("notifyApproval", False))            # type: ignore
        winactor.set_variable($タスク異常通知有無$, result.get("notifyTask", False))          # type: ignore
        winactor.set_variable($WinActor異常通知有無$, result.get("notifyWinactor", False))    # type: ignore
        winactor.set_variable($WinActor接続数上限通知有無$, result.get("notifyWinactorLimit", False))      # type: ignore
        winactor.set_variable($未所属WinActor接続通知有無$, result.get("notifyUndefinedWinactor", False))  # type: ignore
        winactor.set_variable($WinActorライセンス期限通知有無$, result.get("notifyWinactorLicense", False))# type: ignore
        winactor.set_variable($通信量超過通知有無$, result.get("notifyTraffic", False))       # type: ignore
        winactor.set_variable($ストレージ使用量超過通知有無$, result.get("notifyStorage", False))            # type: ignore
        winactor.set_variable($ライセンス数上限通知有無$, result.get("notifyRemainingLicense", False))        # type: ignore
        winactor.set_variable($表示件数$, result.get("pageSize", 0))                          # type: ignore
        winactor.set_variable($多要素認証利用有無$, result.get("mfa", False))                  # type: ignore
        winactor.set_variable($多要素認証方式$, result.get("mfaKind", ""))                    # type: ignore
        winactor.set_variable($WinActorID$, result.get("winactorId", ""))                     # type: ignore
    else:
        # 失敗時は空値やデフォルト値をセット
        winactor.set_variable($ユーザID$, "")                              # type: ignore
        winactor.set_variable($ユーザ名$, "")                              # type: ignore
        winactor.set_variable($親所属ID$, 0)                             # type: ignore
        winactor.set_variable($子所属ID$, 0)                             # type: ignore
        winactor.set_variable($孫所属ID$, 0)                             # type: ignore
        winactor.set_variable($所属名$, "")                              # type: ignore
        winactor.set_variable($ステータス$, "")                          # type: ignore
        winactor.set_variable($権限名$, "")                              # type: ignore
        winactor.set_variable($説明$, "")                                # type: ignore
        winactor.set_variable($オートログアウト$, 0)                     # type: ignore
        winactor.set_variable($役職$, "")                                # type: ignore
        winactor.set_variable($連続ログイン失敗回数$, 0)                 # type: ignore
        winactor.set_variable($最終ログイン失敗日時$, 0)                 # type: ignore
        winactor.set_variable($最終ログイン日時$, 0)                    # type: ignore
        winactor.set_variable($作成日時$, 0)                            # type: ignore
        winactor.set_variable($作成者ユーザID$, "")                     # type: ignore
        winactor.set_variable($更新日時$, 0)                            # type: ignore
        winactor.set_variable($メールアドレス$, "")                     # type: ignore
        winactor.set_variable($承認通知有無$, False)                    # type: ignore
        winactor.set_variable($タスク異常通知有無$, False)              # type: ignore
        winactor.set_variable($WinActor異常通知有無$, False)            # type: ignore
        winactor.set_variable($WinActor接続数上限通知有無$, False)      # type: ignore
        winactor.set_variable($未所属WinActor接続通知有無$, False)      # type: ignore
        winactor.set_variable($WinActorライセンス期限通知有無$, False)  # type: ignore
        winactor.set_variable($通信量超過通知有無$, False)             # type: ignore
        winactor.set_variable($ストレージ使用量超過通知有無$, False)    # type: ignore
        winactor.set_variable($ライセンス数上限通知有無$, False)        # type: ignore
        winactor.set_variable($表示件数$, 0)                            # type: ignore
        winactor.set_variable($多要素認証利用有無$, False)              # type: ignore
        winactor.set_variable($多要素認証方式$, "")                    # type: ignore
        winactor.set_variable($WinActorID$, "")                        # type: ignore