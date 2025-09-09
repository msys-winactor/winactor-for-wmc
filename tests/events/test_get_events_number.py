# tests/events/test_get_events_number.py
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
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
        del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"total": 100, "items": []}

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

    # client.get 呼び出しの params を検証
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

    assert result == {"total": 100, "items": []}


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
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
        del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"total": 50, "items": []}

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

    assert result == {"total": 50, "items": []}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # すべてNone -> モジュールは部門取得を呼ばない
    mock_client.get.return_value = {"total": 0, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    # dn1..3 が全て未指定のため、部門取得は呼ばれない
    mock_get_departments.get_departments.assert_not_called()
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "department1" not in params
    assert "department2" not in params
    assert "department3" not in params

    assert result == {"total": 0, "items": []}


def test_run_list_params_are_normalized(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 25, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        # カンマ区切りの文字列を渡す
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
    assert result == {"total": 25, "items": []}


def test_run_params_dict_and_allowed_filtering(mocker):
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 75, "items": []}

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
    # unknown は除外
    assert "unknown" not in params
    # 許可キーは残る + list 化
    assert params["department1"] == "1"
    assert params["level[]"] == ["1", "2"]
    assert params["page"] == 2
    assert params["size"] == 50
    assert result == {"total": 75, "items": []}


def test_run_skip_department_lookup_when_ids_already_given(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 10, "items": []}

    # department_name1 を渡しても、department1 が既にある場合は解決スキップ
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
    assert result == {"total": 10, "items": []}


def test_run_departments_url_override_used(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 5, "items": []}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
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
    assert result == {"total": 5, "items": []}


def test_run_missing_credentials_returns_empty(mocker):
    # WMCApiClient をモック
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 100, "items": []}

    # base_url/token のいずれかが不足・空文字なら {} を返す
    res1 = get_events_number.run(token="dummy_token")  # base_url なし
    res2 = get_events_number.run(base_url="https://example.com")  # token なし
    res3 = get_events_number.run(base_url="", token="dummy_token")  # base_url 空文字
    res4 = get_events_number.run(
        base_url="https://example.com", token=""
    )  # token 空文字

    assert res1 == {}
    assert res2 == {}
    assert res3 == {}
    assert res4 == {}

    # 空白のみの文字列は truthy のため、現行実装では API が呼ばれる
    res5 = get_events_number.run(base_url="   ", token="dummy_token")
    res6 = get_events_number.run(base_url="https://example.com", token="   ")
    assert res5 == {"total": 100, "items": []}
    assert res6 == {"total": 100, "items": []}

    # 空白ケースの2回だけクライアント生成される
    assert mock_client_class.call_count == 2
    # /events が2回呼ばれている
    assert mock_client.get.call_count == 2


def test_run_department_names_not_found_raises_error(mocker):
    # ラッパー関数が無い場合で、すべて None が返される場合はエラー
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mocker.patch("winactor_for_wmc.events.get_events_number.WMCApiClient")

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
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
    # ラッパー関数が存在する場合はそれを使用
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
    mock_client.get.return_value = {"total": 15, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
    )

    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"total": 15, "items": []}


def test_run_params_vs_kwargs_priority(mocker):
    # params と kwargs の両方が指定された場合、params が優先される（setdefault の動作）
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 30, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        params={"page": 1, "size": 10},  # params が優先される
        page=2,  # setdefault により無視される
        level="3",  # allowed に無いため無視される
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    # params が優先される（setdefault の動作）
    assert params["page"] == 1  # params の値が優先
    assert params["size"] == 10
    # allowed に "level" は無いため含まれない
    assert "level" not in params
    assert result == {"total": 30, "items": []}


def test_run_whitespace_department_names_normalized(mocker):
    # 前後空白の処理をテスト
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
        del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"total": 8, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="  A  ",  # 前後空白
        department_name2="   ",  # 空白のみ → None
        department_name3="",  # 空文字列 → None
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once_with(
        {"items": []},
        department_name1="A",  # 空白除去
        department_name2=None,  # 空白のみは None
        department_name3=None,  # 空文字列は None
    )
    assert result == {"total": 8, "items": []}


def test_run_all_allowed_params(mocker):
    # 許可されたすべてのパラメータをテスト
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 200, "items": []}

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
    assert result == {"total": 200, "items": []}


def test_run_list_params_from_various_types(mocker):
    # リスト系パラメータの様々な入力形式をテスト
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 45, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        **{
            "level[]": [1, 2, 3],  # リスト
            "label[]": (4, 5),  # タプル
            "winactorId[]": {"wa001"},  # セット
        },
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    assert params["level[]"] == [1, 2, 3]
    assert params["label[]"] == [4, 5]
    assert params["winactorId[]"] == ["wa001"]
    assert result == {"total": 45, "items": []}


def test_get_number_success():
    # 正常なレスポンスから total を取得
    result = {"total": 150, "items": []}
    assert get_events_number.get_number(result) == 150


def test_get_number_string_total():
    # total が文字列の場合も int 化される
    result = {"total": "250", "items": []}
    assert get_events_number.get_number(result) == 250


def test_get_number_missing_total():
    # total が存在しない場合は 0
    result = {"items": []}
    assert get_events_number.get_number(result) == 0


def test_get_number_invalid_total():
    # total が数値化できない場合は 0
    result = {"total": "invalid", "items": []}
    assert get_events_number.get_number(result) == 0


def test_get_number_none_total():
    # total が None の場合は 0
    result = {"total": None, "items": []}
    assert get_events_number.get_number(result) == 0


def test_get_number_invalid_result():
    # result が dict でない場合は 0
    assert get_events_number.get_number(None) == 0
    assert get_events_number.get_number([]) == 0
    assert get_events_number.get_number("invalid") == 0
    assert get_events_number.get_number(123) == 0


def test_get_number_zero_total():
    # total が 0 の場合
    result = {"total": 0, "items": []}
    assert get_events_number.get_number(result) == 0


def test_get_number_negative_total():
    # total が負の数の場合
    result = {"total": -5, "items": []}
    assert get_events_number.get_number(result) == -5


def test__norm_various_inputs():
    # _norm 関数のテスト
    norm = get_events_number._norm
    assert norm(None) is None
    assert norm("") is None
    assert norm("   ") is None
    assert norm("  A  ") == "A"
    assert norm(123) == "123"
    assert norm(0) == "0"


def test__ensure_list_various_inputs():
    el = get_events_number._ensure_list
    assert el(None) == []
    assert el([]) == []
    assert el(("a", "b")) == ["a", "b"]
    assert el({"x"}) == ["x"]
    assert el("") == []
    assert el("   ") == []  # 空白のみ
    assert el("a, b ,c") == ["a", "b", "c"]
    assert el(10) == [10]


def test__safe_int_various_inputs():
    si = get_events_number._safe_int
    assert si("10") == 10
    assert si(20) == 20
    assert si("bad", default=5) == 5
    assert si(None, default=-1) == -1
    assert si("", default=100) == 100
    assert si([], default=200) == 200


def test_run_departments_url_in_params_dict_override_used(mocker):
    # params dict 内に departments_url を指定した場合でも、部門取得に使われる
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 12, "items": []}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
        del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events_number.run(
        base_url="https://api-base",
        token="dummy_token",
        params={"departments_url": "https://dep-base"},  # params 側で指定
        department_name1="A",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://dep-base", token="dummy_token"
    )
    assert result == {"total": 12, "items": []}


def test_run_params_value_overrides_kwargs_via_setdefault(mocker):
    # params に入っている値が kwargs より優先される（setdefault の動作）
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 60, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        params={"department1": "1", "page": 3},
        department1="999",  # 無視される（params 優先）
        page=10,  # 無視される（params 優先）
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert params["department1"] == "1"
    assert params["page"] == 3
    assert result == {"total": 60, "items": []}


def test_run_only_department_name3_is_resolved(mocker):
    # department_name3 のみ指定された場合に、department3 が補完される
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events_number.get_departments"
    )
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 22, "items": []}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, "3")
    # ラッパー関数が存在しないことを明示的に設定
    if hasattr(mock_get_departments, "get_departments_ids_by_names_or_error"):
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
    assert result == {"total": 22, "items": []}


def test_run_unallowed_kwargs_are_filtered_out(mocker):
    # allowed に含まれないキーは params に落ちない
    mocker.patch("winactor_for_wmc.events.get_events_number.get_departments")
    mock_client_class = mocker.patch(
        "winactor_for_wmc.events.get_events_number.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"total": 5, "items": []}

    result = get_events_number.run(
        base_url="https://example.com",
        token="dummy_token",
        unknown1="x",
        unknown2="y",
        # "level" は allowed にない（このモジュールの仕様）
        level="3",
        # 許可されているキー
        message="hello",
    )

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert "unknown1" not in params
    assert "unknown2" not in params
    assert "level" not in params  # 非許可
    assert params["message"] == "hello"
    assert result == {"total": 5, "items": []}
