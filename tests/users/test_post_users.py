# tests/users/test_post_users.py
import os
import sys

import pytest

# ライブラリパス追加（プロジェクトルートを先頭に）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from winactor_for_wmc.users import post_users


def test_run_all_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.users.post_users.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", "2", "3")
    mock_client.post.return_value = {"result": "OK"}

    user_data = {}

    result = post_users.run(
        base_url="https://example.com",  # ← ここを修正
        token="dummy_token",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.post.assert_called_once()  # 引数は下で詳細確認

    # 実際にPOSTに渡されたdataを検証（実装側で新しいdictに詰め替えられるため）
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "1"
    assert posted_data["department2"] == "2"
    assert posted_data["department3"] == "3"
    assert result == {"result": "OK"}

    # 呼び出し側の user_data は空のまま（in-place 更新されない）
    assert user_data == {}


def test_run_partial_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.users.post_users.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    mock_client.post.return_value = {"result": "OK"}

    user_data = {}

    result = post_users.run(
        base_url="https://example.com",  # ← ここを修正
        token="dummy_token",
        user_data=user_data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "1"
    assert "department2" not in posted_data
    assert "department3" not in posted_data
    assert result == {"result": "OK"}

    # 呼び出し側は変化しない
    assert user_data == {}


def test_run_only_department2(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.users.post_users.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName2": "B", "department2": "2"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = (None, "2", None)
    mock_client.post.return_value = {"result": "OK"}

    user_data = {}

    result = post_users.run(
        base_url="https://example.com",  # ← ここを修正
        token="dummy_token",
        user_data=user_data,
        department_name1=None,
        department_name2="B",
        department_name3=None,
    )

    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department2"] == "2"
    assert "department1" not in posted_data
    assert "department3" not in posted_data
    assert result == {"result": "OK"}
    assert user_data == {}


def test_run_only_department3(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.users.post_users.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName3": "C", "department3": "3"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, "3")
    mock_client.post.return_value = {"result": "OK"}

    user_data = {}

    result = post_users.run(
        base_url="https://example.com",  # ← ここを修正
        token="dummy_token",
        user_data=user_data,
        department_name1=None,
        department_name2=None,
        department_name3="C",
    )

    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department3"] == "3"
    assert "department1" not in posted_data
    assert "department2" not in posted_data
    assert result == {"result": "OK"}
    assert user_data == {}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.users.post_users.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}
    user_data = {}

    result = post_users.run(
        base_url="https://example.com",  # ← ここを修正
        token="dummy_token",
        user_data=user_data,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    # get_departmentsは呼ばれない
    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == {}
    assert result == {"result": "OK"}
    assert user_data == {}


def test_run_none_user_data(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.users.post_users.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}

    result = post_users.run(
        base_url="https://example.com",  # ← ここを修正
        token="dummy_token",
        user_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == {}
    assert result == {"result": "OK"}
