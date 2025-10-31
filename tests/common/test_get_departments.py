import pytest

from winactor_for_wmc.common import get_departments

# ------------------------------
# get_departments のテスト
# ------------------------------


def test_get_departments_defaults_size_always(mocker):
    # size 未指定時はデフォルト 10000 が常に付与される
    mock_client_class = mocker.patch(
        "winactor_for_wmc.common.get_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"items": []}

    result = get_departments.get_departments(
        base_url="https://example.com",
        token="dummy",
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy")
    mock_client.get.assert_called_once()
    args, kwargs = mock_client.get.call_args
    assert args == ("/departments",)
    assert kwargs["params"] == {"size": 10000}
    assert result == {"items": []}


def test_get_departments_all_params_included(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.common.get_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"items": []}

    result = get_departments.get_departments(
        base_url="https://example.com",
        token="dummy",
        idType="perfect",
        id="id123",
        department1="1",
        department2="2",
        department3="3",
        page=2,
        size=20,
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy")
    mock_client.get.assert_called_once_with(
        "/departments",
        params={
            "idType": "perfect",
            "id": "id123",
            "department1": "1",
            "department2": "2",
            "department3": "3",
            "page": 2,
            "size": 20,
        },
    )
    assert result == {"items": []}


def test_get_departments_empty_strings_ignored_and_page_zero_included(mocker):
    # 空文字は除外され、page=0 は含まれる。size は常に付与される。
    mock_client_class = mocker.patch(
        "winactor_for_wmc.common.get_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"items": []}

    result = get_departments.get_departments(
        base_url="https://example.com",
        token="dummy",
        id="",  # 除外される
        department1="",  # 除外される
        department3=None,  # 除外される
        page=0,  # 含める（None ではない）
        # size 未指定 → 10000
    )

    called_params = mock_client.get.call_args[1]["params"]
    assert called_params == {"page": 0, "size": 10000}
    assert result == {"items": []}


def test_get_departments_base_url_none_calls_client(mocker):
    # base_url=None でも WMCApiClient は呼ばれる（例外発生の有無はクライアント実装依存）
    mock_client_class = mocker.patch(
        "winactor_for_wmc.common.get_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"items": []}

    result = get_departments.get_departments(base_url=None, token="dummy")

    mock_client_class.assert_called_once_with(None, "dummy")
    mock_client.get.assert_called_once_with("/departments", params={"size": 10000})
    assert result == {"items": []}


def test_get_departments_whitespace_values_are_included(mocker):
    # get_departments はトリムせず truthy 判定。空白のみ文字列もパラメータに含まれることを確認。
    mock_client_class = mocker.patch(
        "winactor_for_wmc.common.get_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"items": []}

    result = get_departments.get_departments(
        base_url="https://example.com",
        token="dummy",
        idType="  ",
        id="  ",
        department2="   ",
        # page は未指定、size も未指定 → size は 10000
    )

    args, kwargs = mock_client.get.call_args
    assert args == ("/departments",)
    # 空白のみでも truthy のためそのまま含まれる
    assert kwargs["params"] == {
        "idType": "  ",
        "id": "  ",
        "department2": "   ",
        "size": 10000,
    }
    assert result == {"items": []}


# ------------------------------
# get_departments_ids_by_names のテスト（厳格版）
# ------------------------------


def test_ids_by_names_all_none_params():
    # 何も指定がなければすべて None
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            }
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(result)
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_whitespace_only_treated_as_none():
    # 空白のみは None として扱われる
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            }
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="   ", department_name2="", department_name3=""
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_child_without_parent_raises_error():
    # 子指定で親未指定はエラー
    result = {"items": [{"departmentName2": "B", "department2": "2"}]}

    with pytest.raises(
        ValueError, match="子所属を指定する場合は親所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(result, department_name2="B")


def test_ids_by_names_grandchild_without_parent_and_child_raises_error():
    # 孫指定で親・子両方未指定はエラー
    result = {"items": [{"departmentName3": "C", "department3": "3"}]}

    with pytest.raises(
        ValueError, match="孫所属を指定する場合は親所属と子所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(result, department_name3="C")


def test_ids_by_names_grandchild_with_parent_only_raises_error():
    # 孫指定で親のみ指定（子未指定）もエラー
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName3": "C",
                "department3": "3",
            }
        ]
    }

    with pytest.raises(
        ValueError, match="孫所属を指定する場合は親所属と子所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(
            result, department_name1="A", department_name3="C"
        )


def test_ids_by_names_no_match_raises_error():
    # 指定した所属が見つからない場合はエラー
    result = {"items": [{"departmentName1": "A", "department1": "1"}]}

    with pytest.raises(ValueError, match="指定された所属が見つかりません"):
        get_departments.get_departments_ids_by_names(result, department_name1="X")


def test_ids_by_names_parent_only_success():
    # 親のみ指定で一意に定まる場合
    result = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName1": "A", "department1": "1"},  # 同一ID
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A"
    )
    assert (d1, d2, d3) == ("1", None, None)


def test_ids_by_names_parent_only_ambiguous_raises_error():
    # 親のみ指定で複数の異なるIDが存在する場合はエラー
    result = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName1": "A", "department1": "2"},
        ]
    }

    with pytest.raises(
        ValueError, match="指定された所属が一意に定まりません（親のみ）"
    ):
        get_departments.get_departments_ids_by_names(result, department_name1="A")


def test_ids_by_names_parent_only_null_id_raises_error():
    # 親IDが None の場合はエラー
    result = {
        "items": [
            {"departmentName1": "A", "department1": None},
        ]
    }

    with pytest.raises(ValueError, match="親所属が解決できません"):
        get_departments.get_departments_ids_by_names(result, department_name1="A")


def test_ids_by_names_parent_and_child_success():
    # 親+子指定で一意に定まる場合
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
            },
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
            },  # 同一
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A", department_name2="B"
    )
    assert (d1, d2, d3) == ("1", "2", None)


def test_ids_by_names_parent_and_child_ambiguous_raises_error():
    # 親+子指定で複数の異なる組み合わせが存在する場合はエラー
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
            },
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "9",
            },
        ]
    }

    with pytest.raises(
        ValueError, match="指定された所属が一意に定まりません（親\\+子）"
    ):
        get_departments.get_departments_ids_by_names(
            result, department_name1="A", department_name2="B"
        )


def test_ids_by_names_parent_and_child_null_parent_id_raises_error():
    # 親IDが None の場合はエラー
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": None,
                "departmentName2": "B",
                "department2": "2",
            },
        ]
    }

    with pytest.raises(ValueError, match="親所属が解決できません"):
        get_departments.get_departments_ids_by_names(
            result, department_name1="A", department_name2="B"
        )


def test_ids_by_names_parent_and_child_null_child_id_raises_error():
    # 子IDが None の場合はエラー
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": None,
            },
        ]
    }

    with pytest.raises(ValueError, match="子所属が解決できません"):
        get_departments.get_departments_ids_by_names(
            result, department_name1="A", department_name2="B"
        )


def test_ids_by_names_full_match_success():
    # 3階層すべて指定で成功
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            }
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A", department_name2="B", department_name3="C"
    )
    assert (d1, d2, d3) == ("1", "2", "3")


def test_ids_by_names_full_match_picks_first_when_same():
    # 3階層すべて指定時、同一IDの場合は先頭を採用
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "10",
                "departmentName2": "B",
                "department2": "20",
                "departmentName3": "C",
                "department3": "30",
            },
            {
                "departmentName1": "A",
                "department1": "10",
                "departmentName2": "B",
                "department2": "20",
                "departmentName3": "C",
                "department3": "30",
            },
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A", department_name2="B", department_name3="C"
    )
    assert (d1, d2, d3) == ("10", "20", "30")


def test_ids_by_names_full_match_ambiguous_raises_error():
    # 3階層すべて指定時、異なるIDの組み合わせが存在する場合はエラー
    result = {
        "items": [
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            },
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "9",  # 異なる孫ID
            },
        ]
    }

    with pytest.raises(
        ValueError, match="指定された所属が一意に定まりません（親\\+子\\+孫）"
    ):
        get_departments.get_departments_ids_by_names(
            result, department_name1="A", department_name2="B", department_name3="C"
        )


def test_ids_by_names_trim_and_comparison():
    # 入力・データ側ともに空白はトリムして比較
    result = {
        "items": [
            {
                "departmentName1": "  A ",
                "department1": "1",
                "departmentName2": "B ",
                "department2": "2",
                "departmentName3": " C",
                "department3": "3",
            }
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1=" A  ", department_name2="B", department_name3="C "
    )
    assert (d1, d2, d3) == ("1", "2", "3")


def test_ids_by_names_non_string_inputs_and_items():
    # 非文字列（int）を入力・データ側に混在させ、正規化の非文字列分岐をカバー
    result = {
        "items": [
            {"departmentName1": 100, "department1": "X"},
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1=100
    )
    assert (d1, d2, d3) == ("X", None, None)


def test_ids_by_names_no_items_key_or_none_items():
    # items キーなし
    d1, d2, d3 = get_departments.get_departments_ids_by_names({})
    assert (d1, d2, d3) == (None, None, None)

    # items が None
    d1, d2, d3 = get_departments.get_departments_ids_by_names({"items": None})
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_empty_items_with_specification_raises_error():
    # items は空だが指定がある場合はエラー
    result = {"items": []}

    with pytest.raises(ValueError, match="指定された所属が見つかりません"):
        get_departments.get_departments_ids_by_names(result, department_name1="A")


def test_ids_by_names_child_and_grandchild_without_parent_raises_error():
    # 子+孫指定で親未指定はエラー（子指定の事前チェックで引っかかる）
    result = {
        "items": [
            {
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            }
        ]
    }

    with pytest.raises(
        ValueError, match="子所属を指定する場合は親所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(
            result, department_name2="B", department_name3="C"
        )


# 注意：以下のテストケースは実際のコードでは事前チェックによりエラーになるため、
# 孫のみ指定の分岐には到達しません。コードには分岐が存在しますが、実際には実行されません。


def test_ids_by_names_grandchild_only_would_be_success_but_blocked_by_precheck():
    # 孫のみ指定で一意に定まる場合（事前チェックでブロックされる）
    result = {
        "items": [
            {"departmentName3": "C", "department3": "3"},
            {"departmentName3": "C", "department3": "3"},  # 同一ID
        ]
    }

    # 事前チェックでエラーになる
    with pytest.raises(
        ValueError, match="孫所属を指定する場合は親所属と子所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(result, department_name3="C")


def test_ids_by_names_grandchild_only_would_be_ambiguous_but_blocked_by_precheck():
    # 孫のみ指定で複数の異なるIDが存在する場合（事前チェックでブロックされる）
    result = {
        "items": [
            {"departmentName3": "C", "department3": "3"},
            {"departmentName3": "C", "department3": "9"},
        ]
    }

    # 事前チェックでエラーになる
    with pytest.raises(
        ValueError, match="孫所属を指定する場合は親所属と子所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(result, department_name3="C")


def test_ids_by_names_grandchild_only_would_be_null_but_blocked_by_precheck():
    # 孫IDが None の場合（事前チェックでブロックされる）
    result = {
        "items": [
            {"departmentName3": "C", "department3": None},
        ]
    }

    # 事前チェックでエラーになる
    with pytest.raises(
        ValueError, match="孫所属を指定する場合は親所属と子所属も指定してください"
    ):
        get_departments.get_departments_ids_by_names(result, department_name3="C")


def test_ids_by_names_fallback_error_unreachable():
    # 最後のフォールバックエラーは理論上到達しない
    # すべてのケースが上記の分岐で処理されるため
    # このテストは実際には実行できない（到達不可能なコード）
    pass
