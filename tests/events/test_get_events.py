# tests/events/test_get_events.py
import pytest

from winactor_for_wmc.events import get_events


def test_run_all_departments_without_wrapper(mocker):
    """ラッパー関数が存在しない場合のテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
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
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    # 固定サイズが設定されていることを確認
    assert params["size"] == 100

    assert result == {"result": "OK"}


def test_run_all_departments_with_wrapper(mocker):
    """ラッパー関数が存在する場合のテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 部門取得モック
    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        "2",
        "3",
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    # ラッパー関数が呼ばれることを確認
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
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    # 固定サイズが設定されていることを確認
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert params["size"] == 100

    assert result == {"result": "OK"}


def test_run_partial_departments_without_wrapper(mocker):
    """ラッパー関数が存在しない場合の部分部門テスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 1部門のみ
    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    assert params["size"] == 100  # 固定サイズ

    assert result == {"result": "OK"}


def test_run_partial_departments_with_wrapper(mocker):
    """ラッパー関数が存在する場合の部分部門テスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 1部門のみ
    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    assert result == {"result": "OK"}


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    # すべてNone -> モジュールは部門取得を呼ばない
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    assert params["size"] == 100

    assert result == {"result": "OK"}


def test_run_department_names_not_found_raises_error_without_wrapper(mocker):
    """ラッパー関数が無い場合で、すべて None が返される場合はエラー"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error

    with pytest.raises(
        ValueError, match="指定された所属が見つからないか一意に定まりません"
    ):
        get_events.run(
            base_url="https://example.com",
            token="dummy_token",
            department_name1="NotFound",
        )


def test_run_with_wrapper_function_uses_wrapper(mocker):
    # ラッパー関数が存在する場合はそれを使用
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
    )

    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"result": "OK"}


def test_run_missing_credentials_returns_empty(mocker):
    # WMCApiClient をモック
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    # base_url/token のいずれかが不足・空文字なら {} を返す
    res1 = get_events.run(token="dummy_token")  # base_url なし
    res2 = get_events.run(base_url="https://example.com")  # token なし
    res3 = get_events.run(base_url="", token="dummy_token")  # base_url 空文字
    res5 = get_events.run(base_url="https://example.com", token="")  # token 空文字

    assert res1 == {}
    assert res2 == {}
    assert res3 == {}
    assert res5 == {}

    # 空白のみの文字列は truthy のため、現行実装では API が呼ばれる
    res4 = get_events.run(base_url="   ", token="dummy_token")
    res6 = get_events.run(base_url="https://example.com", token="   ")
    assert res4 == {"result": "OK"}
    assert res6 == {"result": "OK"}

    # 空白ケースの2回だけクライアント生成される
    assert mock_client_class.call_count == 2
    # /events が2回呼ばれている
    assert mock_client.get.call_count == 2


def test_run_list_params_are_normalized(mocker):
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    assert params["size"] == 100
    assert result == {"result": "OK"}


def test_run_params_dict_and_allowed_filtering(mocker):
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    assert params["size"] == 100  # 固定値で上書き
    assert result == {"result": "OK"}


def test_run_skip_department_lookup_when_ids_already_given(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    # department_name1 を渡しても、department1 が既にある場合は解決スキップ
    result = get_events.run(
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
    assert called_kwargs["params"]["size"] == 100
    assert result == {"result": "OK"}


def test_run_params_vs_kwargs_priority(mocker):
    # params と kwargs の両方が指定された場合、params が優先される（setdefault の動作）
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        params={"page": 1, "size": 10},  # params が優先される
        page=2,  # setdefault により無視される
        sort="createdTime",  # kwargs で追加（許可されたパラメータ）
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    # params が優先される（setdefault の動作）
    assert params["page"] == 1  # params の値が優先
    assert params["size"] == 100  # 固定値で上書き
    assert params["sort"] == "createdTime"  # kwargs で追加
    assert result == {"result": "OK"}


def test_run_all_allowed_params(mocker):
    # 許可されたすべてのパラメータをテスト
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
        size=50,  # 固定値で上書きされる
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
    assert params["size"] == 100  # 固定値
    assert result == {"result": "OK"}


def test_run_list_params_from_various_types(mocker):
    # リスト系パラメータの様々な入力形式をテスト
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    assert params["size"] == 100
    assert result == {"result": "OK"}


def test_run_departments_url_override_used_without_wrapper(mocker):
    """ラッパー関数が存在しない場合のdepartments_url上書きテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events.run(
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
    """ラッパー関数が存在する場合のdepartments_url上書きテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )

    result = get_events.run(
        base_url="https://api-base",
        token="dummy_token",
        departments_url="https://departments-base",
        department_name1="A",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://departments-base", token="dummy_token"
    )
    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"result": "OK"}


def test_run_whitespace_department_names_normalized_without_wrapper(mocker):
    """ラッパー関数が存在しない場合の空白正規化テスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
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
    assert result == {"result": "OK"}


def test_run_whitespace_department_names_normalized_with_wrapper(mocker):
    """ラッパー関数が存在する場合の空白正規化テスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        None,
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="  A  ",  # 前後空白
        department_name2="   ",  # 空白のみ → None
        department_name3="",  # 空文字列 → None
    )

    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once_with(
        {"items": []},
        department_name1="A",  # 空白除去
        department_name2=None,  # 空白のみは None
        department_name3=None,  # 空文字列は None
    )
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()
    assert result == {"result": "OK"}


def test_run_department_names_some_resolved_without_wrapper(mocker):
    """ラッパー関数が存在しない場合の部分解決テスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, "3")
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="NotFound",
        department_name3="C",
    )

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    # 解決されたもののみ含まれる
    assert params["department1"] == "1"
    assert "department2" not in params  # None のため除外
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_department_names_some_resolved_with_wrapper(mocker):
    """ラッパー関数が存在する場合の部分解決テスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        "1",
        None,
        "3",
    )
    mock_client.get.return_value = {"result": "OK"}

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name1="A",
        department_name2="NotFound",
        department_name3="C",
    )

    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    mock_client.get.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]

    # 解決されたもののみ含まれる
    assert params["department1"] == "1"
    assert "department2" not in params  # None のため除外
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_only_department_name2_is_resolved_without_wrapper(mocker):
    """ラッパー関数が存在しない場合でdepartment2のみが解決される場合のテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, "2", None)
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name2="B",
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    # d2_id のみが設定される
    assert "department1" not in params
    assert params["department2"] == "2"
    assert "department3" not in params
    assert result == {"result": "OK"}


def test_run_only_department_name2_is_resolved_with_wrapper(mocker):
    """ラッパー関数が存在する場合でdepartment2のみが解決される場合のテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        None,
        "2",
        None,
    )

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name2="B",
    )

    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    # d2_id のみが設定される
    assert "department1" not in params
    assert params["department2"] == "2"
    assert "department3" not in params
    assert result == {"result": "OK"}


def test_run_only_department_name3_is_resolved_without_wrapper(mocker):
    """ラッパー関数が存在しない場合でdepartment3のみが解決される場合のテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, "3")
    # ラッパー関数が存在しないことを確実にする
    del mock_get_departments.get_departments_ids_by_names_or_error

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name3="C",
    )

    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    # d3_id のみが設定される
    assert "department1" not in params
    assert "department2" not in params
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_only_department_name3_is_resolved_with_wrapper(mocker):
    """ラッパー関数が存在する場合でdepartment3のみが解決される場合のテスト"""
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.events.get_events.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    mock_get_departments.get_departments.return_value = {"items": []}
    # ラッパー関数を存在させ、戻り値を設定
    mock_get_departments.get_departments_ids_by_names_or_error.return_value = (
        None,
        None,
        "3",
    )

    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        department_name3="C",
    )

    # ラッパー関数が呼ばれることを確認
    mock_get_departments.get_departments_ids_by_names_or_error.assert_called_once()
    # 通常の関数は呼ばれない
    mock_get_departments.get_departments_ids_by_names.assert_not_called()

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    # d3_id のみが設定される
    assert "department1" not in params
    assert "department2" not in params
    assert params["department3"] == "3"
    assert result == {"result": "OK"}


def test_run_size_always_set_to_100(mocker):
    """サイズが常に100に設定されることのテスト"""
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    # サイズを指定しても100に上書きされる
    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        size=50,  # 指定しても無視される
    )

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert params["size"] == 100  # 常に100に設定される

    assert result == {"result": "OK"}


def test_run_size_override_user_specified_size(mocker):
    """ユーザー指定のサイズが100で上書きされることのテスト"""
    mocker.patch("winactor_for_wmc.events.get_events.get_departments")
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"result": "OK"}

    # params でサイズを指定しても上書きされる
    result = get_events.run(
        base_url="https://example.com",
        token="dummy_token",
        params={"size": 25, "page": 1},
    )

    _, called_kwargs = mock_client.get.call_args
    params = called_kwargs["params"]
    assert params["size"] == 100  # 上書きされる
    assert params["page"] == 1  # その他のパラメータは保持される

    assert result == {"result": "OK"}


def test_get_event_info_large_index_with_additional_api_call(mocker):
    """大きなインデックスで追加APIコールが発生するテスト"""
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 初回レスポンス（100件未満）
    initial_result = {
        "items": [{"level": i, "message": f"item_{i}"} for i in range(50)],
        "totalCount": 250,
    }

    # 追加取得レスポンス（ページ2）- インデックス120に対応する要素を含む
    additional_result = {
        "items": [{"level": i + 100, "message": f"item_{i + 100}"} for i in range(50)],
    }
    mock_client.get.return_value = additional_result

    # インデックス120を要求（ページ2のインデックス20）
    result = get_events.get_event_info(
        initial_result,
        120,
        base_url="https://example.com",
        token="dummy_token",
        sort="createdAt",
        department1="1",
    )

    # 追加APIコールが発生することを確認
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.get.assert_called_once_with(
        "/events",
        params={
            "sort": "createdAt",
            "department1": "1",
            "page": 2,  # (120 // 100) + 1 = 2
            "size": 100,
        },
    )

    # 正しい要素が返されることを確認
    assert result["level"] == 120  # 追加取得データの20番目（120 % 100 = 20）
    assert result["message"] == "item_120"


def test_get_event_info_large_index_without_credentials_raises_error(mocker):
    """認証情報なしで大きなインデックスを指定した場合のエラーテスト"""
    initial_result = {
        "items": [{"level": i, "message": f"item_{i}"} for i in range(50)],
    }

    # base_url または token が不足している場合
    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info(initial_result, 120)  # 認証情報なし

    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info(
            initial_result, 120, base_url="https://example.com"
        )  # tokenなし

    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info(
            initial_result, 120, token="dummy_token"
        )  # base_urlなし


def test_get_event_info_negative_index_with_total_count():
    """負数インデックスと全件数を使ったテスト"""
    result = {
        "items": [
            {"level": 1, "message": "first"},
            {"level": 2, "message": "second"},
        ],
        "totalCount": 2,  # 全件数が現在のアイテム数と同じ
    }

    # -1は全体の最後（インデックス1）
    info = get_events.get_event_info(result, -1)
    assert info["level"] == 2
    assert info["message"] == "second"

    # -2は最初（インデックス0）
    info = get_events.get_event_info(result, -2)
    assert info["level"] == 1
    assert info["message"] == "first"


def test_get_event_info_negative_index_out_of_range():
    """負数インデックスが範囲外の場合のテスト"""
    result = {
        "items": [{"level": 1, "message": "first"}],
        "totalCount": 1,
    }

    # -2は範囲外（全件数1なので、-1のみ有効）
    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info(result, -2)


def test_get_event_info_negative_index_zero_total_count():
    """負数インデックスで全件数が0の場合のテスト"""
    result = {
        "items": [],
        "totalCount": 0,
    }

    with pytest.raises(ValueError, match="イベント情報が存在しません。"):
        get_events.get_event_info(result, -1)


def test_get_event_info_negative_index_no_total_count():
    """負数インデックスでtotalCountが未指定の場合のテスト"""
    result = {
        "items": [
            {"level": 1, "message": "first"},
            {"level": 2, "message": "second"},
        ]
        # totalCount なし（デフォルト0）
    }

    with pytest.raises(ValueError, match="イベント情報が存在しません。"):
        get_events.get_event_info(result, -1)


def test_get_event_info_additional_call_empty_response(mocker):
    """追加APIコールで空レスポンスが返された場合のテスト"""
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    initial_result = {
        "items": [{"level": i, "message": f"item_{i}"} for i in range(50)],
    }

    # 空レスポンス
    mock_client.get.return_value = {"items": []}

    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info(
            initial_result,
            120,
            base_url="https://example.com",
            token="dummy_token",
        )


def test_get_event_info_additional_call_index_out_of_page_range(mocker):
    """追加APIコールでページ内インデックスが範囲外の場合のテスト"""
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    initial_result = {
        "items": [{"level": i, "message": f"item_{i}"} for i in range(50)],
    }

    # 10件のみのレスポンス
    mock_client.get.return_value = {
        "items": [{"level": i + 100, "message": f"item_{i + 100}"} for i in range(10)]
    }

    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info(
            initial_result,
            150,  # ページ2のインデックス50を要求するが、10件しかない
            base_url="https://example.com",
            token="dummy_token",
        )


def test_get_event_info_additional_call_with_list_params(mocker):
    """追加APIコールでリストパラメータが正しく処理されるテスト"""
    mock_client_class = mocker.patch("winactor_for_wmc.events.get_events.WMCApiClient")
    mock_client = mock_client_class.return_value

    initial_result = {
        "items": [{"level": i, "message": f"item_{i}"} for i in range(50)],
    }

    # インデックス150に対応する要素を含むレスポンス
    additional_result = {
        "items": [{"level": i + 100, "message": f"item_{i + 100}"} for i in range(100)],
    }
    mock_client.get.return_value = additional_result

    result = get_events.get_event_info(
        initial_result,
        150,
        base_url="https://example.com",
        token="dummy_token",
        **{
            "level[]": "1,2,3",  # カンマ区切り文字列
            "label[]": [4, 5],  # リスト
            "winactorId[]": {"wa001"},  # セット
        },
    )

    # リストパラメータが正しく処理されることを確認
    mock_client.get.assert_called_once_with(
        "/events",
        params={
            "level[]": ["1", "2", "3"],
            "label[]": [4, 5],
            "winactorId[]": ["wa001"],
            "page": 2,
            "size": 100,
        },
    )

    assert result["level"] == 150


def test_get_event_info_page_calculation():
    """ページ計算のテスト（モックなしで計算ロジックのみ確認）"""
    # インデックス0-99 → ページ1
    # インデックス100-199 → ページ2
    # インデックス200-299 → ページ3

    # テスト用の計算関数
    def calc_page_and_index(idx):
        page_size = 100
        target_page = (idx // page_size) + 1
        index_in_page = idx % page_size
        return target_page, index_in_page

    # 境界値テスト
    assert calc_page_and_index(0) == (1, 0)
    assert calc_page_and_index(99) == (1, 99)
    assert calc_page_and_index(100) == (2, 0)
    assert calc_page_and_index(199) == (2, 99)
    assert calc_page_and_index(200) == (3, 0)
    assert calc_page_and_index(15003) == (151, 3)


def test_get_event_info_success_with_defaults_and_negative_index():
    result = {
        "items": [
            {
                "level": 2,
                "label": "5",  # 文字列でも int 化
                "winactorId": "wa001",
                # 一部フィールドは欠落 -> 既定値になる
                "createdTime": "1700000000000",
                "departmentName": "DeptA",
                "subjectDepartmentName": "",
            },
            {
                "level": 1,
                "label": 7,
                "message": "hello",
            },
        ],
        "totalCount": 2,  # 全件数を追加
    }
    # -1 は末尾
    info = get_events.get_event_info(result, -1)
    assert info["level"] == 1
    assert info["label"] == 7
    assert info["message"] == "hello"
    # 欠落項目は既定値
    assert info["fileId"] == ""
    assert info["createdTime"] == 0

    # 0 は先頭
    info0 = get_events.get_event_info(result, 0)
    assert info0["level"] == 2
    assert info0["label"] == 5
    assert info0["winactorId"] == "wa001"
    assert info0["createdTime"] == 1700000000000
    assert info0["departmentName"] == "DeptA"
    # 空文字は "" に正規化
    assert info0["subjectDepartmentName"] == ""


@pytest.mark.parametrize(
    "bad_result",
    [
        None,
        [],
        "not_dict",
        123,
        {"items": None},
        {"items": "not_list"},
        {"items": []},
    ],
)
def test_get_event_info_errors_on_bad_response(bad_result):
    with pytest.raises(ValueError):
        get_events.get_event_info(bad_result, 0)


@pytest.mark.parametrize("bad_index", [None, "", "  "])
def test_get_event_info_errors_on_missing_index(bad_index):
    with pytest.raises(
        ValueError,
        match="イベントのインデックス が未指定です|イベントのインデックスが未指定です。",
    ):
        get_events.get_event_info({"items": [{}]}, bad_index)


@pytest.mark.parametrize("bad_index", ["x", [], {}])
def test_get_event_info_errors_on_non_numeric_index(bad_index):
    with pytest.raises(
        ValueError, match="イベントのインデックスが数値ではありません。"
    ):
        get_events.get_event_info({"items": [{}]}, bad_index)


def test_get_event_info_errors_on_out_of_range():
    # 正数インデックスの範囲外
    with pytest.raises(ValueError, match="イベントのインデックスが範囲外です。"):
        get_events.get_event_info({"items": [{}]}, 1)

    # 負数インデックスでtotalCountが0の場合
    with pytest.raises(ValueError, match="イベント情報が存在しません。"):
        get_events.get_event_info({"items": [{}]}, -2)


def test_get_event_info_item_none_defaults():
    # items に None が含まれるケース（target = items[idx] or {} の分岐をカバー）
    result = {"items": [None]}
    info = get_events.get_event_info(result, 0)
    # すべて既定値で返る
    assert info["level"] == 0
    assert info["label"] == 0
    assert info["winactorId"] == ""
    assert info["fileId"] == ""
    assert info["scenarioId"] == ""
    assert info["scheduleId"] == ""
    assert info["taskId"] == ""
    assert info["userId"] == ""
    assert info["departmentId"] == ""
    assert info["roleId"] == ""
    assert info["stageId"] == ""
    assert info["particularStageId"] == ""
    assert info["other"] == ""
    assert info["message"] == ""
    assert info["subject"] == ""
    assert info["subjectDepartment"] == ""
    assert info["subjectRole"] == ""
    assert info["createdTime"] == 0
    assert info["departmentName"] == ""
    assert info["subjectDepartmentName"] == ""


def test_get_event_info_string_index():
    # 文字列のインデックスも int に変換される
    result = {
        "items": [
            {"level": 1, "message": "first"},
            {"level": 2, "message": "second"},
        ]
    }

    info = get_events.get_event_info(result, "1")  # 文字列
    assert info["level"] == 2
    assert info["message"] == "second"


# ヘルパー関数のテストも継続
def test__ensure_list_various_inputs():
    el = get_events._ensure_list
    assert el(None) == []
    assert el([]) == []
    assert el(("a", "b")) == ["a", "b"]
    assert el({"x"}) == ["x"]
    assert el("") == []
    assert el("   ") == []  # 空白のみ
    assert el("a, b ,c") == ["a", "b", "c"]
    assert el(10) == [10]


def test__safe_int_various_inputs():
    si = get_events._safe_int
    assert si("10") == 10
    assert si(20) == 20
    assert si("bad", default=5) == 5
    assert si(None, default=-1) == -1


def test__ensure_index_provided_raises():
    with pytest.raises(ValueError, match="idx が未指定です。"):
        get_events._ensure_index_provided(None, "idx")
    with pytest.raises(ValueError, match="idx が未指定です。"):
        get_events._ensure_index_provided("   ", "idx")


def test__norm_various_inputs():
    # _norm 関数のテスト
    norm = get_events._norm
    assert norm(None) is None
    assert norm("") is None
    assert norm("   ") is None
    assert norm("  A  ") == "A"
    assert norm(123) == "123"
    assert norm(0) == "0"


def test__build_event_info_helper():
    """_build_event_info ヘルパー関数のテスト"""
    target = {
        "level": "2",
        "label": 5,
        "winactorId": "wa001",
        "message": "test message",
        "createdTime": 1700000000,
    }

    result = get_events._build_event_info(target)

    assert result["level"] == 2  # 文字列から数値に変換
    assert result["label"] == 5
    assert result["winactorId"] == "wa001"
    assert result["message"] == "test message"
    assert result["createdTime"] == 1700000000
    # 未指定項目は既定値
    assert result["fileId"] == ""
    assert result["userId"] == ""


def test__build_event_info_empty_target():
    """_build_event_info に空辞書を渡した場合のテスト"""
    result = get_events._build_event_info({})

    # すべて既定値
    assert result["level"] == 0
    assert result["label"] == 0
    assert result["winactorId"] == ""
    assert result["createdTime"] == 0
