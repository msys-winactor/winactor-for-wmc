import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.departments import delete_departments


def main(**kwargs):
    # run関数の呼び出し
    return delete_departments.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    DEPARTMENT_ID = !所属ID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, department_id=DEPARTMENT_ID)