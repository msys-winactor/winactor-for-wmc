import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.winactors import delete_winactors

def main(**kwargs):
    # run関数の呼び出し
    return delete_winactors.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    WINACTOR_ID = !WinActorID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, winactor_id=WINACTOR_ID)
