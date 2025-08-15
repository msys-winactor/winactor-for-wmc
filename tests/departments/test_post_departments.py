# tests/departments/test_post_departments.py
import os
import sys

import pytest

# ライブラリパス追加（プロジェクトルートを先頭に）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from winactor_for_wmc.departments import post_departments


def test_run_parent_and_child_sets_both(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("10", "20", None)
    mock_client.post.return_value = {"result": "OK"}

    department_data = {}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2="Child",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.post.assert_called_once()  # 引数は下で詳細確認

    # 実際にPOSTに渡されたdataを検証（実装側で新しいdictに詰め替えられる想定）
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert posted_data["department2"] == "20"
    assert result == {"result": "OK"}

    # 呼び出し側の department_data は空のまま（in-place 更新されない想定）
    assert department_data == {}


def test_run_parent_only_sets_department1(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("10", None, None)
    mock_client.post.return_value = {"result": "OK"}

    department_data = {}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2=None,
    )

    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert "department2" not in posted_data
    assert result == {"result": "OK"}

    # 呼び出し側は変化しない
    assert department_data == {}


def test_run_child_only_sets_nothing(mocker):
    # 親未入力・子のみ入力 → 階層IDは付与されない想定
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}

    department_data = {}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1=None,
        department_name2="Child",
    )

    # 親が未入力のため get_departments は呼ばれない
    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == {}  # 階層IDは付与されない
    assert result == {"result": "OK"}
    assert department_data == {}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}
    department_data = {}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1=None,
        department_name2=None,
    )

    # get_departmentsは呼ばれない
    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == {}
    assert result == {"result": "OK"}
    assert department_data == {}


def test_run_none_department_data(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.post.return_value = {"result": "OK"}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=None,
        department_name1=None,
        department_name2=None,
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once()
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == {}
    assert result == {"result": "OK"}
