import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.tasks import delete_tasks

def main(**kwargs):
    # run関数の呼び出し
    return delete_tasks.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    TASK_ID = !タスクID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, task_id=TASK_ID)