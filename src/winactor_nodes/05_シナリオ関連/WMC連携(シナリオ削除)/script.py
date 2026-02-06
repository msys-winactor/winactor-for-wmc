import sys

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.scenarios import delete_scenarios

def main(**kwargs):
    # run関数の呼び出し
    return delete_scenarios.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    SCENARIO_ID = !シナリオID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, scenario_id=SCENARIO_ID)
