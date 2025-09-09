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

    department_data = {"existing": "data"}  # 非空辞書を使用

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
    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="Parent",
        department_name2="Child",
        department_name3=None,
    )
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    # POSTに渡されるデータを確認
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert posted_data["department2"] == "20"
    assert posted_data["existing"] == "data"

    # department_data は in-place で更新される
    assert department_data["department1"] == "10"
    assert department_data["department2"] == "20"
    assert department_data["existing"] == "data"
    assert result == {"result": "OK"}


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

    department_data = {"existing": "data"}  # 非空辞書を使用

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2=None,
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="Parent",
        department_name2=None,
        department_name3=None,
    )

    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert "department2" not in posted_data
    assert posted_data["existing"] == "data"

    assert department_data["department1"] == "10"
    assert "department2" not in department_data
    assert department_data["existing"] == "data"
    assert result == {"result": "OK"}


def test_run_parent_only_with_empty_child_name(mocker):
    # 親指定、子は空文字列 → 親のみとして処理
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

    department_data = {"existing": "data"}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2="",  # 空文字列
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="Parent",
        department_name2=None,  # 空文字列は None に正規化される
        department_name3=None,
    )

    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"

    assert department_data["department1"] == "10"
    assert result == {"result": "OK"}


def test_run_child_only_raises_error(mocker):
    # 子のみ指定はエラー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )

    department_data = {}

    with pytest.raises(
        ValueError, match="子所属を指定する場合は親所属も指定してください"
    ):
        post_departments.run(
            base_url="https://example.com",
            token="dummy_token",
            department_data=department_data,
            department_name1=None,
            department_name2="Child",
        )

    # get_departments は呼ばれない
    mock_get_departments.get_departments.assert_not_called()


def test_run_child_only_with_empty_parent_raises_error(mocker):
    # 親が空文字列、子が指定されている場合もエラー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )

    department_data = {}

    with pytest.raises(
        ValueError, match="子所属を指定する場合は親所属も指定してください"
    ):
        post_departments.run(
            base_url="https://example.com",
            token="dummy_token",
            department_data=department_data,
            department_name1="",  # 空文字列
            department_name2="Child",
        )

    mock_get_departments.get_departments.assert_not_called()


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

    # get_departments は呼ばれない
    mock_get_departments.get_departments.assert_not_called()
    mock_client.post.assert_called_once_with("/departments", data={})
    assert department_data == {}
    assert result == {"result": "OK"}


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
    mock_client.post.assert_called_once_with("/departments", data={})
    assert result == {"result": "OK"}


def test_run_parent_not_found_raises_error(mocker):
    # 親所属が見つからない場合はエラー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)

    department_data = {}

    with pytest.raises(
        ValueError, match="親所属が見つかりません: department_name1=Parent"
    ):
        post_departments.run(
            base_url="https://example.com",
            token="dummy_token",
            department_data=department_data,
            department_name1="Parent",
            department_name2=None,
        )

    mock_get_departments.get_departments.assert_called_once()


def test_run_child_not_found_raises_error(mocker):
    # 親・子とも指定されているのに子が見つからない場合はエラー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.departments.post_departments.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.post_departments.WMCApiClient"
    )

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("10", None, None)

    department_data = {}

    with pytest.raises(
        ValueError, match="子所属が見つかりません: department_name2=Child（親: Parent）"
    ):
        post_departments.run(
            base_url="https://example.com",
            token="dummy_token",
            department_data=department_data,
            department_name1="Parent",
            department_name2="Child",
        )

    mock_get_departments.get_departments.assert_called_once()


def test_run_whitespace_handling(mocker):
    # 前後空白の処理をテスト
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

    department_data = {"existing": "data"}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="  Parent  ",  # 前後空白
        department_name2="  Child  ",  # 前後空白
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="Parent",  # 空白が除去される
        department_name2="Child",  # 空白が除去される
        department_name3=None,
    )

    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert posted_data["department2"] == "20"
    assert result == {"result": "OK"}


def test_run_non_string_input_handling(mocker):
    # 非文字列入力の処理をテスト
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

    department_data = {"existing": "data"}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1=123,  # 数値
        department_name2=None,
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="123",  # 文字列に変換される
        department_name2=None,
        department_name3=None,
    )

    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert result == {"result": "OK"}


def test_run_existing_department_data_preserved(mocker):
    # 既存の department_data が保持されることをテスト
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

    department_data = {"departmentName": "TestDept", "description": "Test Description"}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2="Child",
    )

    expected_data = {
        "departmentName": "TestDept",
        "description": "Test Description",
        "department1": "10",
        "department2": "20",
    }

    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data == expected_data
    assert department_data == expected_data
    assert result == {"result": "OK"}


def test_run_parent_found_child_empty_string(mocker):
    # 親が見つかり、子が空文字列の場合
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

    department_data = {"existing": "data"}

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2="   ",  # 空白のみ
    )

    # 空白のみは空文字列に正規化され、None として扱われる
    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="Parent",
        department_name2=None,
        department_name3=None,
    )

    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert "department2" not in posted_data

    assert department_data["department1"] == "10"
    assert "department2" not in department_data
    assert result == {"result": "OK"}


def test_run_empty_department_data_not_modified_inplace(mocker):
    # 空辞書の場合、`department_data or {}` により新しい辞書が作成され、元は変更されない
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

    department_data = {}  # 空辞書

    result = post_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_data=department_data,
        department_name1="Parent",
        department_name2="Child",
    )

    # POSTには正しいデータが渡される
    posted_data = mock_client.post.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert posted_data["department2"] == "20"

    # しかし、元の空辞書は変更されない（`department_data or {}` の動作）
    assert department_data == {}
    assert result == {"result": "OK"}
