import requests


class GetDepartmentsError(Exception):
    """APIエラー時の独自例外"""

    pass


def get_departments(
    url,
    token,
    idType=None,
    id=None,
    department1=None,
    department2=None,
    department3=None,
    page=None,
    size=None,
):
    headers = {"Authorization": token}
    params = {}

    if idType:
        params["idType"] = idType
    if id:
        params["id"] = id
    if department1:
        params["department1"] = department1
    if department2:
        params["department2"] = department2
    if department3:
        params["department3"] = department3
    if page is not None:
        params["page"] = page
    if size is not None:
        params["size"] = size

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_json = response.json()
            # ここでシンプルな文字列で例外を投げる
            raise GetDepartmentsError(
                f"module: get_departments\n"
                f"status_code: {response.status_code}\n"
                f"error: {error_json.get('error', '')}\n"
                f"detail: {error_json.get('detail', '')}"
            )

    except Exception as e:
        # すでにGetDepartmentsErrorなら再raise、それ以外はstr(e)で投げる
        if isinstance(e, GetDepartmentsError):
            raise
        raise GetDepartmentsError(str(e))


def get_department_ids_by_names(
    result, department_name1=None, department_name2=None, department_name3=None
):
    """
    取得した所属一覧から部門名でIDを取得する
    """
    department1_value = None
    department2_value = None
    department3_value = None

    for item in result.get("items", []):
        if (
            department1_value is None
            and department_name1
            and item.get("departmentName1") == department_name1
        ):
            department1_value = item.get("department1")
        if (
            department2_value is None
            and department_name2
            and item.get("departmentName2") == department_name2
        ):
            department2_value = item.get("department2")
        if (
            department3_value is None
            and department_name3
            and item.get("departmentName3") == department_name3
        ):
            department3_value = item.get("department3")
        if (
            (department_name1 is None or department1_value is not None)
            and (department_name2 is None or department2_value is not None)
            and (department_name3 is None or department3_value is not None)
        ):
            break

    return department1_value, department2_value, department3_value
