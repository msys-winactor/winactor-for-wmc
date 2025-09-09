# tests/scenarios/test_put_scenarios.py

import pytest

from winactor_for_wmc.scenarios import put_scenarios


def test_run_all_departments(mocker):
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", "2", "3")
    client.put.return_value = {"result": "OK"}

    scenario_data = {}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="dummy",
        scenario_id="sid-123",
        scenario_data=scenario_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    gd.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy"
    )
    gd.get_departments_ids_by_names.assert_called_once()
    client_cls.assert_called_once_with("https://example.com", "dummy")
    client.put.assert_called_once()
    # エンドポイントが正しいか確認
    assert client.put.call_args.kwargs["data"] == {
        "department1": "1",
        "department2": "2",
        "department3": "3",
    }
    assert client.put.call_args.args[0].endswith("/scenarios/sid-123")
    # 呼び出し元の空 dict は or {} により変更されない
    assert scenario_data == {}
    assert result == {"result": "OK"}


def test_run_partial_departments_only_parent(mocker):
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", None, None)
    client.put.return_value = {"result": "OK"}

    scenario_data = {}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-1",
        scenario_data=scenario_data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"department1": "1"}
    assert scenario_data == {}  # in-place 更新なし
    assert result == {"result": "OK"}


def test_run_only_department2(mocker):
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "2", None)
    client.put.return_value = {"result": "OK"}

    scenario_data = {}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-2",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"department2": "2"}
    assert scenario_data == {}  # in-place 更新なし
    assert result == {"result": "OK"}


def test_run_only_department3(mocker):
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, "3")
    client.put.return_value = {"result": "OK"}

    scenario_data = {}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-3",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2=None,
        department_name3="C",
    )

    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"department3": "3"}
    assert scenario_data == {}  # in-place 更新なし
    assert result == {"result": "OK"}


def test_run_no_departments_defaults_added(mocker):
    # 3つとも falsy → 既定値を付与。ただし呼び出し側 scenario_data は空 dict なので in-place 反映されない
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value
    client.put.return_value = {"result": "OK"}

    scenario_data = {}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-4",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    gd.get_departments.assert_not_called()
    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"department1": 0, "department2": None, "department3": None}
    assert scenario_data == {}  # or {} により別インスタンス使用のため変更されない
    assert result == {"result": "OK"}


def test_run_none_scenario_data_defaults_added(mocker):
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value
    client.put.return_value = {"result": "OK"}

    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-5",
        scenario_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_not_called()
    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"department1": 0, "department2": None, "department3": None}
    assert result == {"result": "OK"}


def test_run_with_department_names_but_no_match_adds_nothing(mocker):
    # 指定はあるが、ID 解決が全て None → 追加なし
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.put.return_value = {"result": "OK"}

    scenario_data = {"name": "test_scenario"}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-6",
        scenario_data=scenario_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"name": "test_scenario"}
    assert scenario_data == {"name": "test_scenario"}
    assert result == {"result": "OK"}


def test_run_whitespace_name_triggers_lookup_but_adds_nothing(mocker):
    # スペースのみは truthy → ルックアップは実施されるが、None が返れば追加されない
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.put.return_value = {"result": "OK"}

    scenario_data = {"name": "test_scenario2"}
    result = put_scenarios.run(
        base_url=None,  # None でもクライアント生成される
        token="t",
        scenario_id="sid-7",
        scenario_data=scenario_data,
        department_name1="   ",  # truthy
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_called_once_with(base_url=None, token="t")
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"name": "test_scenario2"}
    assert result == {"result": "OK"}


def test_run_ids_zero_and_empty_string_are_put(mocker):
    # 0 と "" は None ではない → 追加される。ただし呼び出し側の空 dict は変更されない
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (0, "", None)
    client.put.return_value = {"result": "OK"}

    scenario_data = {}
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-8",
        scenario_data=scenario_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {"department1": 0, "department2": ""}
    assert scenario_data == {}  # 空 dict のため in-place 反映されない
    assert result == {"result": "OK"}


def test_run_overwrites_existing_department_fields(mocker):
    # 既存の値は新しい ID で上書き（None はスキップ）。呼び出し側が truthy dict のため in-place 反映される
    gd = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "22", None)
    client.put.return_value = {"result": "OK"}

    scenario_data = {
        "department1": "old1",
        "department2": "old2",
        "name": "keep_scenario",
    }
    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-9",
        scenario_data=scenario_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    posted = client.put.call_args.kwargs["data"]
    assert posted == {
        "department1": "old1",
        "department2": "22",
        "name": "keep_scenario",
    }
    assert scenario_data == {
        "department1": "old1",
        "department2": "22",
        "name": "keep_scenario",
    }
    assert result == {"result": "OK"}


def test_run_no_departments_with_non_empty_scenario_data_inplace_update(mocker):
    # 3つとも falsy ＋ scenario_data が非空 dict → 既定値が in-place で追加されるブランチ
    mocker.patch("winactor_for_wmc.scenarios.put_scenarios.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.scenarios.put_scenarios.WMCApiClient")
    client = client_cls.return_value
    client.put.return_value = {"result": "OK"}

    scenario_data = {"name": "keep_scenario"}  # 非空で渡す

    result = put_scenarios.run(
        base_url="https://example.com",
        token="t",
        scenario_id="sid-10",
        scenario_data=scenario_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    client.put.assert_called_once()
    posted = client.put.call_args.kwargs["data"]
    assert posted == {
        "name": "keep_scenario",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    # in-place 反映されることを確認
    assert scenario_data == {
        "name": "keep_scenario",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    assert result == {"result": "OK"}
