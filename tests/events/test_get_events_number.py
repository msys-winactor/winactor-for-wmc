# tests/events/test_get_events_number.py

import pytest

from winactor_for_wmc.events import get_events_number


def test_run_all_departments_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", "2", "3")
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error

    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {
            "items": [
                {"departmentName1": "A", "department1": "1"},
                {"departmentName2": "B", "department2": "2"},
                {"departmentName3": "C", "department3": "3"},
            ]
        },
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    mock_client.get.assert_called_once()
    called_endpoint, called_kwargs = (
        mock_client.get.call_args[0][0],
        mock_client.get.call_args[1],
    )
    assert called_endpoint == "/events"
    params = called_kwargs["params"]
    assert params["department1"] == "1"
    assert params["department2"] == "2"
    assert params["department3"] == "3"

    assert result == {"result": "OK"}


def test_run_all_departments_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        "2",
        "3",
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once_with(
        {
            "items": [
                {"departmentName1": "A", "department1": "1"},
                {"departmentName2": "B", "department2": "2"},
                {"departmentName3": "C", "department3": "3"},
            ]
        },
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    assert result == {"result": "OK"}


def test_run_partial_departments_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert params["department1"] == "1"
    assert "department2" not in params
    assert "department3" not in params

    assert result == {"result": "OK"}


def test_run_partial_departments_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    assert result == {"result": "OK"}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert "department2" not in params
    assert "department3" not in params

    assert result == {"result": "OK"}


def test_run_department_names_not_found_raises_error_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mocker.patch("winactor_for_wmc.events.get_events_number.WMCApiClient")

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)
    del mock_get_departments.get_departments_ids_by_names_or_error

    with pytest.raises(
        ValueError, match="指定された所属が見つからないか一意に定まりません"
    ):
        get_events_number.run(
            base_url="https://example.com",
            token="dummy_token",
            department_name1="NotFound",
        )


def test_run_with_wrapper_function_uses_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"result": "OK"}


def test_run_missing_credentials_returns_empty(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    res1 = get_events_number.run(token="dummy_token")
    res2 = get_events_number.run(base_url="https://example.com")
    res3 = get_events_number.run(base_url="", token="dummy_token")
    res5 = get_events_number.run(base_url="https://example.com", token="")

    assert res1 == {}
    assert res2 == {}
    assert res3 == {}
    assert res5 == {}

    res4 = get_events_number.run(base_url="   ", token="dummy_token")
    res6 = get_events_number.run(base_url="https://example.com", token="   ")
    assert res4 == {"result": "OK"}
    assert res6 == {"result": "OK"}

    assert mock_client_class.call_count == 2
    assert mock_client.get.call_count == 2


def test_run_list_params_are_normalized(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        **{
            "level[]": "0, 1,3",
            "label[]": "10,20",
            "winactorId[]": "wa001, wa002",
        },
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["level[]"] == ["0", "1", "3"]
    assert params["label[]"] == ["10", "20"]
    assert params["winactorId[]"] == ["wa001", "wa002"]
    assert result == {"result": "OK"}


def test_run_params_dict_and_allowed_filtering(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        params={
            "department1": "1",
            "unknown": "should_be_ignored",
            "level[]": "1,2",
            "page": 2,
            "size": 50,
        },
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "unknown" not in params
    assert params["department1"] == "1"
    assert params["level[]"] == ["1", "2"]
    assert params["page"] == 2
    assert params["size"] == 50
    assert result == {"result": "OK"}


def test_run_skip_department_lookup_when_ids_already_given(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department1="999",
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    assert called_kwargs["params"]["department1"] == "999"
    assert result == {"result": "OK"}


def test_run_params_vs_kwargs_priority(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        params={"page": 1, "size": 10},
        page=2,
        sort="createdTime",
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["page"] == 1
    assert params["size"] == 10
    assert params["sort"] == "createdTime"
    assert result == {"result": "OK"}


def test_run_all_allowed_params(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department1="1",
        department2="2",
        department3="3",
        createdAtType="range",
        createdAtDate1="2023-01-01",
        createdAtTime1="09:00",
        createdAtDate2="2023-12-31",
        createdAtTime2="18:00",
        messageType="contains",
        message="error",
        sort="createdTime",
        sortDirection="desc",
        page=1,
        size=100,
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["department1"] == "1"
    assert params["department2"] == "2"
    assert params["department3"] == "3"
    assert params["createdAtType"] == "range"
    assert params["createdAtDate1"] == "2023-01-01"
    assert params["createdAtTime1"] == "09:00"
    assert params["createdAtDate2"] == "2023-12-31"
    assert params["createdAtTime2"] == "18:00"
    assert params["messageType"] == "contains"
    assert params["message"] == "error"
    assert params["sort"] == "createdTime"
    assert params["sortDirection"] == "desc"
    assert params["page"] == 1
    assert params["size"] == 100
    assert result == {"result": "OK"}


def test_run_list_params_from_various_types(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        **{
            "level[]": [1, 2, 3],
            "label[]": (4, 5),
            "winactorId[]": {"wa001"},
        },
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["level[]"] == [1, 2, 3]
    assert params["label[]"] == [4, 5]
    assert params["winactorId[]"] == ["wa001"]
    assert result == {"result": "OK"}


def test_run_departments_url_override_used_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events_number.run(
        base_url="https://api-base",
        token="dummy_token",
        departments_url="https://departments-base",
        department_name1="A",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://departments-base", token="dummy_token"
    )
    assert result == {"result": "OK"}


def test_run_departments_url_override_used_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )

    result = get_events_number.run(
        base_url="https://api-base",
        token="dummy_token",
        departments_url="https://departments-base",
        department_name1="A",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://departments-base", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"result": "OK"}


def test_run_whitespace_department_names_normalized_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="  A  ",
        department_name2="   ",
        department_name3="",
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )
    assert result == {"result": "OK"}


def test_run_whitespace_department_names_normalized_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="  A  ",
        department_name2="   ",
        department_name3="",
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once_with(
        {"items": []},
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"result": "OK"}


def test_run_department_names_some_resolved_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, "3")
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="NotFound",
        department_name3="C",
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["department1"] == "1"
    assert "department2" not in params
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_department_names_some_resolved_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        "3",
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="NotFound",
        department_name3="C",
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["department1"] == "1"
    assert "department2" not in params
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_only_department_name2_is_resolved_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, "2", None)
    del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name2="B",
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert params["department2"] == "2"
    assert "department3" not in params
    assert result == {"result": "OK"}


def test_run_only_department_name2_is_resolved_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        None,
        "2",
        None,
    )

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name2="B",
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert params["department2"] == "2"
    assert "department3" not in params
    assert result == {"result": "OK"}


def test_run_only_department_name3_is_resolved_without_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, "3")
    del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name3="C",
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert "department2" not in params
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_only_department_name3_is_resolved_with_wrapper(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        None,
        None,
        "3",
    )

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name3="C",
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert "department2" not in params
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_get_number_success_and_various_inputs():
    # 正常ケース
    assert get_events_number.get_number({"total": 123}) == 123
    # total が文字列
    assert get_events_number.get_number({"total": "456"}) == 456
    # total 欠落 -> 0
    assert get_events_number.get_number({"items": []}) == 0
    # レスポンスが不正 -> 0
    assert get_events_number.get_number(None) == 0
    assert get_events_number.get_number([]) == 0
    assert get_events_number.get_number("bad") == 0
    # total が数値化不可 -> 0
    assert get_events_number.get_number({"total": "x"}) == 0
    # total が float 文字列は int 変換できず -> 0
    assert get_events_number.get_number({"total": "3.14"}) == 0
    # total が float -> int へ
    assert get_events_number.get_number({"total": 3.99}) == 3


def test__ensure_list_various_inputs():
    el = get_events_number._ensure_list
    assert el(None) == []
    assert el([]) == []
    assert el(("a", "b")) == ["a", "b"]
    assert el({"x"}) == ["x"]
    assert el("") == []
    assert el("   ") == []
    assert el("a, b ,c") == ["a", "b", "c"]
    assert el(10) == [10]


def test__safe_int_various_inputs():
    si = get_events_number._safe_int
    assert si("10") == 10
    assert si(20) == 20
    assert si("bad", default=5) == 5
    assert si(None, default=-1) == -1
    assert si(3.14) == 3
    assert si("3.14", default=0) == 0
    assert si("3.14", default=99) == 99


def test__norm_various_inputs():
    norm = get_events_number._norm
    assert norm(None) is None
    assert norm("") is None
    assert norm("   ") is None
    assert norm("  A  ") == "A"
    assert norm(123) == "123"
    assert norm(0) == "0"
