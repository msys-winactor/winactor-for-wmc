import requests

import get_departments


class RegisterScheduleError(Exception):
    """スケジュール登録時の独自例外"""

    pass


def register_schedule_with_department_names(
    schedules_url,
    departments_url,
    token,
    schedule_data,
    department_name1=None,
    department_name2=None,
    department_name3=None,
):
    """
    部門名からIDを取得し、スケジュールを登録する
    """
    # 1. 部門名→ID変換
    try:
        departments_result = get_departments.get_departments(
            url=departments_url, token=token
        )
        department1_id, department2_id, department3_id = (
            get_departments.get_department_ids_by_names(
                departments_result,
                department_name1=department_name1,
                department_name2=department_name2,
                department_name3=department_name3,
            )
        )
        if department1_id is not None:
            schedule_data["department1"] = department1_id
        if department2_id is not None:
            schedule_data["department2"] = department2_id
        if department3_id is not None:
            schedule_data["department3"] = department3_id
    except get_departments.GetDepartmentsError as e:
        # 必要に応じてシンプルに
        raise RegisterScheduleError(str(e))

    # 2. スケジュール登録API呼び出し
    headers = {"Authorization": token}
    try:
        response = requests.post(schedules_url, headers=headers, json=schedule_data)
        if response.status_code == 201:
            return response.json()
        else:
            try:
                error_json = response.json()
            except Exception:
                error_json = {}
            # ここでシンプルなメッセージだけ渡す
            raise RegisterScheduleError(
                f"module: post_schedules\n"
                f"status_code: {response.status_code}\n"
                f"error: {error_json.get('error', '')}\n"
                f"detail: {error_json.get('detail', '')}"
            )
    except Exception as e:
        # requests自体のエラーなど
        raise RegisterScheduleError(str(e))
