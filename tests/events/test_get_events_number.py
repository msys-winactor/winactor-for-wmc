# tests/test_get_events_number.py
import pytest

from winactor_for_wmc.events import get_events_number


def test_run_all_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # 部門取得モック
    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", "2", "3")
    mock_client.get.return_value = {"result": "OK", "total": 10}

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
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
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
    assert result == {"result": "OK", "total": 10}


def test_run_partial_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # 1部門のみ
    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    mock_client.get.return_value = {"result": "OK", "total": 1}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert params["department1"] == "1"
    assert "department2" not in params
    assert "department3" not in params
    assert result == {"result": "OK", "total": 1}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # dn1..3 がすべて None -> 部門取得は行わない
    mock_client.get.return_value = {"result": "OK", "total": 0}

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
    assert result == {"result": "OK", "total": 0}


def test_run_list_params_are_normalized(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK", "total": 3}

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
    assert result == {"result": "OK", "total": 3}


def test_run_params_dict_and_allowed_filtering(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK", "total": 5}

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
    assert result == {"result": "OK", "total": 5}


def test_run_skip_department_lookup_when_ids_already_given(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK", "total": 9}

    # department1 が指定されている場合は lookup をスキップ
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
    assert result == {"result": "OK", "total": 9}


def test_run_departments_url_override_used(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK", "total": 0}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)

    result = get_events_number.run(
        base_url="https://api-base",
        token="dummy_token",
        departments_url="https://departments-base",
        department_name1="A",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://departments-base", token="dummy_token"
    )
    assert result == {"result": "OK", "total": 0}


def test_run_handles_department_lookup_failure(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK", "total": 0}

    # 例外発生しても処理継続
    mock_get_departments.get_departments.side_effect = RuntimeError("boom")

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert result == {"result": "OK", "total": 0}


def test_run_missing_credentials_returns_empty(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK", "total": 1}

    # base_url/token のいずれかが不足・空文字なら {} を返す
    res1 = get_events_number.run(token="dummy_token")  # base_url なし
    res2 = get_events_number.run(base_url="https://example.com")  # token なし
    res3 = get_events_number.run(base_url="", token="dummy_token")  # base_url 空文字
    res5 = get_events_number.run(
        base_url="https://example.com", token=""
    )  # token 空文字

    assert res1 == {}
    assert res2 == {}
    assert res3 == {}
    assert res5 == {}

    # 空白のみは truthy のため現行実装では API を呼び出す
    res4 = get_events_number.run(base_url="   ", token="dummy_token")
    res6 = get_events_number.run(base_url="https://example.com", token="   ")
    assert res4 == {"result": "OK", "total": 1}
    assert res6 == {"result": "OK", "total": 1}

    # 上記2回だけクライアント生成・呼び出し
    assert mock_client_class.call_count == 2
    assert mock_client.get.call_count == 2


def test_get_number_various_inputs():
    # 正常
    assert get_events_number.get_number({"total": 12}) == 12
    # 文字列でも int 化
    assert get_events_number.get_number({"total": "34"}) == 34
    # total 欠落 -> 0
    assert get_events_number.get_number({"items": []}) == 0
    # 不正レスポンス型 -> 0
    assert get_events_number.get_number(None) == 0
    assert get_events_number.get_number([]) == 0
    assert get_events_number.get_number("not dict") == 0


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
