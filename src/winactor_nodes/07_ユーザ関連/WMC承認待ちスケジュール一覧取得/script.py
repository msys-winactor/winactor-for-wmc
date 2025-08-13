import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.users import get_users_approvals

def main(**kwargs):
    return get_users_approvals.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!      # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    USER_NAME = !ユーザ名!     # type: ignore
    INDEX = !インデックス!      # 0始まり。負数も可。 # type: ignore

    result = main(base_url=BASE_URL, token=TOKEN, user_name=USER_NAME)

    schedule_id, schedule_name = get_users_approvals.get_schedule_info(result, INDEX)

    winactor.set_variable($承認待ちスケジュールID$, schedule_id)           # type: ignore
    winactor.set_variable($承認待ちスケジュール名$, schedule_name)          # type: ignore