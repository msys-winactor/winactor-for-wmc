import pytest

from winactor_for_wmc import post_schedules


def setup_common_mocks(mocker, dept_ids=(1, 2, 3)):
    # get_departments.get_departments のモック
    mocker.patch(
        "winactor_for_wmc.post_schedules.get_departments.get_departments",
        return_value={
            "items": [
                {
                    "departmentName1": "営業部",
                    "department1": 1,
                    "departmentName2": "東日本",
                    "department2": 2,
                    "departmentName3": "A班",
                    "department3": 3,
                }
            ]
        },
    )
    # get_departments.get_department_ids_by_names のモック
    mocker.patch(
        "winactor_for_wmc.post_schedules.get_departments.get_department_ids_by_names",
        return_value=dept_ids,
    )


def test_register_schedule_with_department_names_success(mocker):
    setup_common_mocks(mocker)

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "schedule123", "name": "テストスケジュール"}

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post",
        return_value=MockResponse(),
    )
    result = post_schedules.register_schedule_with_department_names(
        "http://dummy/schedules",
        "http://dummy/departments",
        "token",
        {"name": "テストスケジュール"},
        department_name1="営業部",
        department_name2="東日本",
        department_name3="A班",
    )
    assert result == {"id": "schedule123", "name": "テストスケジュール"}


def test_register_schedule_with_department_names_api_error_json(mocker):
    setup_common_mocks(mocker)

    class MockResponse:
        status_code = 400

        def json(self):
            return {"error": "Bad", "detail": "詳細"}

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post",
        return_value=MockResponse(),
    )
    with pytest.raises(post_schedules.RegisterScheduleError) as excinfo:
        post_schedules.register_schedule_with_department_names(
            "http://dummy/schedules",
            "http://dummy/departments",
            "token",
            {"name": "テストスケジュール"},
            department_name1="営業部",
        )
    assert "status_code: 400" in str(excinfo.value)
    assert "Bad" in str(excinfo.value)


def test_register_schedule_with_department_names_api_error_json_decode(mocker):
    setup_common_mocks(mocker)

    class MockResponse:
        status_code = 400

        def json(self):
            raise Exception("json decode error")

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post",
        return_value=MockResponse(),
    )
    with pytest.raises(post_schedules.RegisterScheduleError) as excinfo:
        post_schedules.register_schedule_with_department_names(
            "http://dummy/schedules",
            "http://dummy/departments",
            "token",
            {"name": "テストスケジュール"},
            department_name1="営業部",
        )
    assert "status_code: 400" in str(excinfo.value)


def test_register_schedule_with_department_names_post_exception(mocker):
    setup_common_mocks(mocker)
    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post",
        side_effect=Exception("post error"),
    )
    with pytest.raises(post_schedules.RegisterScheduleError) as excinfo:
        post_schedules.register_schedule_with_department_names(
            "http://dummy/schedules",
            "http://dummy/departments",
            "token",
            {"name": "テストスケジュール"},
            department_name1="営業部",
        )
    assert "post error" in str(excinfo.value)


def test_register_schedule_with_department_names_get_departments_error(mocker):
    mocker.patch(
        "winactor_for_wmc.post_schedules.get_departments.get_departments",
        side_effect=post_schedules.get_departments.GetDepartmentsError(
            "部門取得エラー"
        ),
    )
    with pytest.raises(post_schedules.RegisterScheduleError) as excinfo:
        post_schedules.register_schedule_with_department_names(
            "http://dummy/schedules",
            "http://dummy/departments",
            "token",
            {"name": "テストスケジュール"},
            department_name1="営業部",
        )
    assert "部門取得エラー" in str(excinfo.value)


# --- ここから分岐網羅テスト ---


def test_register_schedule_with_only_department1(mocker):
    setup_common_mocks(mocker, dept_ids=(1, None, None))

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "schedule1"}

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post", return_value=MockResponse()
    )
    result = post_schedules.register_schedule_with_department_names(
        "http://dummy/schedules",
        "http://dummy/departments",
        "token",
        {"name": "テスト"},
        department_name1="営業部",
    )
    assert result == {"id": "schedule1"}


def test_register_schedule_with_only_department2(mocker):
    setup_common_mocks(mocker, dept_ids=(None, 2, None))

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "schedule2"}

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post", return_value=MockResponse()
    )
    result = post_schedules.register_schedule_with_department_names(
        "http://dummy/schedules",
        "http://dummy/departments",
        "token",
        {"name": "テスト"},
        department_name2="東日本",
    )
    assert result == {"id": "schedule2"}


def test_register_schedule_with_only_department3(mocker):
    setup_common_mocks(mocker, dept_ids=(None, None, 3))

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "schedule3"}

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post", return_value=MockResponse()
    )
    result = post_schedules.register_schedule_with_department_names(
        "http://dummy/schedules",
        "http://dummy/departments",
        "token",
        {"name": "テスト"},
        department_name3="A班",
    )
    assert result == {"id": "schedule3"}


def test_register_schedule_with_no_departments(mocker):
    setup_common_mocks(mocker, dept_ids=(None, None, None))

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "schedule0"}

    mocker.patch(
        "winactor_for_wmc.post_schedules.requests.post", return_value=MockResponse()
    )
    result = post_schedules.register_schedule_with_department_names(
        "http://dummy/schedules",
        "http://dummy/departments",
        "token",
        {"name": "テスト"},
    )
    assert result == {"id": "schedule0"}
