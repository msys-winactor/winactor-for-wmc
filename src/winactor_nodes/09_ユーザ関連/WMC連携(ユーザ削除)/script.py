import sys

sys.path.append(r"C:\Users\Public\msys-dx-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.users import delete_users


def main(**kwargs):
    # run関数の呼び出し
    return delete_users.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    USER_NAME = !ユーザ名!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, user_name=USER_NAME)