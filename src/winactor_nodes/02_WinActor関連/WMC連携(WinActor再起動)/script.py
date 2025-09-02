import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.winactors import put_winactors_restart


def main(**kwargs):
    # run関数の呼び出し
    return put_winactors_restart.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!        # type: ignore
    TOKEN = !アクセストークン!    # type: ignore
    WINACTOR_ID = !WinActorID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, winactor_id=WINACTOR_ID)