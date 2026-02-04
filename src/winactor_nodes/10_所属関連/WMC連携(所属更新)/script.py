import sys

sys.path.append(r"C:\Users\Public\msys-dx-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.departments import put_departments


def main(**kwargs):
    return put_departments.run(**kwargs)


if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    DEPARTMENT_ID = !所属ID!  # type: ignore

    NAME = !更新後の所属名!  # type: ignore
    REMARKS = !更新後のメモ!  # type: ignore

    # リクエストボディ作成（未入力は送らない）
    department_data = {}
    if NAME and str(NAME).strip():
        department_data["name"] = str(NAME).strip()
    if REMARKS and str(REMARKS).strip():
        department_data["remarks"] = str(REMARKS).strip()

    # mainの呼び出し
    result = main(
        base_url=BASE_URL,
        token=TOKEN,
        department_id=DEPARTMENT_ID,
        department_data=department_data,
    )