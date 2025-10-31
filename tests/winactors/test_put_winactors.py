# tests/winactors/test_put_winactors.py

import os
import sys

import pytest

# ライブラリパス追加（プロジェクトルートを先頭に）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from winactor_for_wmc.winactors import put_winactors


def test_run_all_empty_departments_sets_defaults_and_calls_put(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {}

    result = put_winactors.run(
        winactor_id="WA-001",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        winactor_data=winactor_data,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    # 3つすべて空欄のため、部門一覧取得は行わない
    mock_get_departments.get_departments.assert_not_called()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once()
    called_endpoint = mock_client.put.call_args.args[0]
    assert called_endpoint == "/winactors/WA-001"

    posted_data = mock_client.put.call_args.kwargs["data"]
    assert posted_data["department1"] == 0
    assert posted_data["department2"] is None
    assert posted_data["department3"] is None
    assert result == {"result": "OK"}

    # 呼び出し側の dict は変更されない（新しい dict を詰め替えて送る想定）
    assert winactor_data == {}


def test_run_parent_and_child_sets_both_ids(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("10", "20", None)
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {}

    result = put_winactors.run(
        winactor_id="WA-002",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        winactor_data=winactor_data,
        department_name1="Parent",
        department_name2="Child",
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once()
    assert mock_client.put.call_args.args[0] == "/winactors/WA-002"

    posted_data = mock_client.put.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert posted_data["department2"] == "20"
    assert "department3" not in posted_data
    assert result == {"result": "OK"}

    # 呼び出し側の dict は変更されない
    assert winactor_data == {}


def test_run_parent_only_sets_department1(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("10", None, None)
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {}

    result = put_winactors.run(
        winactor_id="WA-003",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        winactor_data=winactor_data,
        department_name1="Parent",
        department_name2=None,
        department_name3=None,
    )

    mock_client.put.assert_called_once()
    posted_data = mock_client.put.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert "department2" not in posted_data
    assert "department3" not in posted_data
    assert result == {"result": "OK"}

    # 呼び出し側の dict は変更されない
    assert winactor_data == {}


def test_run_child_only_does_lookup_but_sets_nothing_if_not_found(mocker):
    # 親未入力・子のみ入力 → ルックアップは実行されるが該当が無ければ設定されない
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {}

    result = put_winactors.run(
        winactor_id="WA-004",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        winactor_data=winactor_data,
        department_name1=None,
        department_name2="Child",
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_called_once()
    mock_client.put.assert_called_once()
    posted_data = mock_client.put.call_args.kwargs["data"]
    assert posted_data == {}  # 何も設定されない
    assert result == {"result": "OK"}
    # 呼び出し側の dict は変更されない
    assert winactor_data == {}


def test_run_none_winactor_data_and_all_empty_departments_sets_defaults(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.put.return_value = {"result": "OK"}

    result = put_winactors.run(
        winactor_id="WA-005",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        winactor_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.put.assert_called_once()
    posted_data = mock_client.put.call_args.kwargs["data"]
    assert posted_data["department1"] == 0
    assert posted_data["department2"] is None
    assert posted_data["department3"] is None
    assert result == {"result": "OK"}


def test_run_sets_department3_when_all_three_found(mocker):
    # department3 の分岐（行39）を通すため、3階層すべてが取得できたケース
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("10", "20", "30")
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {}

    result = put_winactors.run(
        winactor_id="WA-006",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token="dummy_token",
        winactor_data=winactor_data,
        department_name1="Parent",
        department_name2="Child",
        department_name3="GrandChild",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once()
    assert mock_client.put.call_args.args[0] == "/winactors/WA-006"

    posted_data = mock_client.put.call_args.kwargs["data"]
    assert posted_data["department1"] == "10"
    assert posted_data["department2"] == "20"
    assert posted_data["department3"] == "30"
    assert result == {"result": "OK"}

    # 呼び出し側の dict は変更されない前提（既存テストに合わせる）
    assert winactor_data == {}


def test_run_names_provided_but_no_departments_url_skips_lookup_and_sets_nothing(
    mocker,
):
    # 部門名はあるが departments_url が無い → ルックアップせず部門キーは付与されない分岐をカバー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {"name": "no-dept-url"}

    result = put_winactors.run(
        winactor_id="WA-007",
        winactors_url="https://example.com",
        departments_url=None,  # URL が無い
        token="dummy_token",
        winactor_data=winactor_data,
        department_name1="Parent",
        department_name2="Child",
        department_name3="GrandChild",
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.put.assert_called_once()
    posted_data = mock_client.put.call_args.kwargs["data"]
    assert "department1" not in posted_data
    assert "department2" not in posted_data
    assert "department3" not in posted_data
    assert posted_data["name"] == "no-dept-url"
    assert result == {"result": "OK"}
    assert winactor_data == {"name": "no-dept-url"}


def test_run_names_provided_but_no_token_skips_lookup_and_sets_nothing(mocker):
    # 部門名はあるが token が無い → ルックアップせず部門キーは付与されない分岐をカバー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    winactor_data = {"name": "no-token"}

    result = put_winactors.run(
        winactor_id="WA-008",
        winactors_url="https://example.com",
        departments_url="https://example.com",
        token=None,  # トークンが無い
        winactor_data=winactor_data,
        department_name1="Parent",
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_not_called()
    mock_client.put.assert_called_once()
    posted_data = mock_client.put.call_args.kwargs["data"]
    assert "department1" not in posted_data
    assert "department2" not in posted_data
    assert "department3" not in posted_data
    assert posted_data["name"] == "no-token"
    assert result == {"result": "OK"}
    assert winactor_data == {"name": "no-token"}
