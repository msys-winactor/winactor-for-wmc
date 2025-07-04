import pytest

from winactor_for_wmc.schedules import post_schedules


def test_run_all_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.schedules.post_schedules.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.schedules.post_schedules.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # 部門取得
    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", "2", "3")
    mock_client.post.return_value = {"result": "OK"}

    schedule_dict = {}

    result = post_schedules.run(
        schedules_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        schedule_data=schedule_dict,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.post.assert_called_once_with("/schedules", data=schedule_dict)
    assert schedule_dict["department1"] == "1"
    assert schedule_dict["department2"] == "2"
    assert schedule_dict["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_partial_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.schedules.post_schedules.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.schedules.post_schedules.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # 1部門のみ
    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    mock_client.post.return_value = {"result": "OK"}

    schedule_dict = {}

    result = post_schedules.run(
        schedules_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        schedule_data=schedule_dict,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    assert schedule_dict["department1"] == "1"
    assert "department2" not in schedule_dict
    assert "department3" not in schedule_dict
    assert result == {"result": "OK"}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.schedules.post_schedules.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.schedules.post_schedules.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # すべてNone
    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)
    mock_client.post.return_value = {"result": "OK"}

    schedule_dict = {}

    result = post_schedules.run(
        schedules_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        schedule_data=schedule_dict,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    assert "department1" not in schedule_dict
    assert "department2" not in schedule_dict
    assert "department3" not in schedule_dict
    assert result == {"result": "OK"}
