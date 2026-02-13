import sys

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.schedules import put_schedules_disable


def main(**kwargs):
    # run関数の呼び出し
    return put_schedules_disable.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    SCHEDULE_ID = !スケジュールID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, schedule_id=SCHEDULE_ID)
