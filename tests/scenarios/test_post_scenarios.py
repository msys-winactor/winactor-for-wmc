# tests/scenarios/test_post_scenarios.py
import os
import sys

import pytest

# ルートをインポートパスに追加（必要に応じて調整）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from winactor_for_wmc.scenarios import post_scenarios


def test_run_all_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # 部門一覧 -> ID 解決
    dep_result = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments.return_value = dep_result
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", "2", "3")
    mock_client.post.return_value = {"result": "OK"}

    scenario_data = {}

    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=scenario_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        dep_result, department_name1="A", department_name2="B", department_name3="C"
    )
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.post.assert_called_once()

    # post に渡された data を検証（空dictを渡してもモジュール側で新規dictに詰め替える実装のため）
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == {"department1": "1", "department2": "2", "department3": "3"}
    assert result == {"result": "OK"}


def test_run_partial_departments_only_name1(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    mock_client.post.return_value = {"result": "OK"}

    data = {}
    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_called_once()
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted == {"department1": "1"}
    assert result == {"result": "OK"}


def test_run_only_department2_id_set_when_others_none(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, "2", None)
    mock_client.post.return_value = {"result": "OK"}

    scenario_data = {}

    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2="B",
        department_name3=None,
    )

    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted == {"department2": "2"}
    assert result == {"result": "OK"}


def test_run_only_department3(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, "3")
    mock_client.post.return_value = {"result": "OK"}

    scenario_data = {}

    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2=None,
        department_name3="C",
    )

    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted == {"department3": "3"}
    assert result == {"result": "OK"}


def test_run_no_departments_names_provided_none(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}
    scenario_data = {"foo": "bar"}

    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    # 名前が一切渡されていないため部門取得は呼ばれない
    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted == {"foo": "bar"}
    assert result == {"result": "OK"}


def test_run_none_scenario_data(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}

    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted == {}
    assert result == {"result": "OK"}


def test_run_empty_string_names_do_not_trigger_lookup(mocker):
    """空文字は偽値として扱われ、部門取得は呼ばれない想定"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.post.return_value = {"result": "OK"}

    data = {}
    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=data,
        department_name1="",
        department_name2="",
        department_name3="",
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted == {}
    assert result == {"result": "OK"}


def test_run_overwrites_existing_department_ids_when_resolved(mocker):
    """scenario_data に既に値があっても、解決したIDで上書きされること"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.post_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    mock_client.post.return_value = {"result": "OK"}

    scenario_data = {"department1": "old"}

    result = post_scenarios.run(
        base_url="https://example.com",
        token="dummy_token",
        scenario_data=scenario_data,
        department_name1="A",  # 解決される -> "1"
        department_name2=None,
        department_name3=None,
    )

    mock_client.post.assert_called_once()
    posted = mock_client.post.call_args.kwargs["data"]
    # 上書きされた値を検証（元の scenario_data は空dictのため or {} により別オブジェクトに詰め替えられる）
    assert posted == {"department1": "1"}
    assert result == {"result": "OK"}
