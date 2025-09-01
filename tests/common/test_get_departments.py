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


# ------------------------------
# get_departments_ids_by_names のテスト
# ------------------------------


def test_ids_by_names_full_match_all_levels():
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


def test_ids_by_names_trim_and_empty_handling():
    # 入力・データ側ともに空白はトリムして比較、空白のみは未指定扱い
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
    # 入力側も両端空白を含める
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1=" A  ", department_name2="B", department_name3="C "
    )
    assert (d1, d2, d3) == ("1", "2", "3")

    # 空白のみは未指定として扱う → 親のみ指定の一意判定にかかる
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1=" A ", department_name2="   ", department_name3=""
    )
    assert (d1, d2, d3) == ("1", None, None)


def test_ids_by_names_parent_only_unique_and_ambiguous():
    result = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName1": "A", "department1": "1"},  # 同一ID → 一意
        ]
    }
    # 親 A の ID が一意（同じ "1"）なら親のみ返す
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A"
    )
    assert (d1, d2, d3) == ("1", None, None)

    # 親 A の ID が異なる候補で複数 → None
    result_amb = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName1": "A", "department1": "2"},
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result_amb, department_name1="A"
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_parent_and_child_unique_and_ambiguous():
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
            {
                "departmentName1": "A",
                "department1": "1",
                "departmentName2": "C",
                "department2": "3",
            },
        ]
    }
    # (親, 子) の組み合わせが一意なら孫は None で返す
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A", department_name2="B"
    )
    assert (d1, d2, d3) == ("1", "2", None)

    # (親, 子) の組み合わせが複数存在 → None
    result_amb = {
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
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result_amb, department_name1="A", department_name2="B"
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_child_only_unique_and_ambiguous():
    result = {
        "items": [
            {"departmentName2": "B", "department2": "2"},
            {"departmentName2": "B", "department2": "2"},  # 同一
            {"departmentName2": "C", "department2": "3"},
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name2="B"
    )
    assert (d1, d2, d3) == (None, "2", None)

    result_amb = {
        "items": [
            {"departmentName2": "B", "department2": "2"},
            {"departmentName2": "B", "department2": "9"},
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result_amb, department_name2="B"
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_child_and_grandchild_unique_and_ambiguous():
    result = {
        "items": [
            {
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            },
            {
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            },  # 同一
            {
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "D",
                "department3": "4",
            },
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name2="B", department_name3="C"
    )
    assert (d1, d2, d3) == (None, "2", "3")

    result_amb = {
        "items": [
            {
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            },
            {
                "departmentName2": "B",
                "department2": "9",
                "departmentName3": "C",
                "department3": "3",
            },
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result_amb, department_name2="B", department_name3="C"
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_grandchild_only_unique_and_ambiguous():
    result = {
        "items": [
            {"departmentName3": "C", "department3": "3"},
            {"departmentName3": "C", "department3": "3"},  # 同一
            {"departmentName3": "D", "department3": "4"},
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name3="C"
    )
    assert (d1, d2, d3) == (None, None, "3")

    result_amb = {
        "items": [
            {"departmentName3": "C", "department3": "3"},
            {"departmentName3": "C", "department3": "9"},
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result_amb, department_name3="C"
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_full_match_picks_first_when_multiple():
    # 3階層すべて指定時は候補の先頭を採用
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
                "department1": "1",
                "departmentName2": "B",
                "department2": "2",
                "departmentName3": "C",
                "department3": "3",
            },
        ]
    }
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A", department_name2="B", department_name3="C"
    )
    assert (d1, d2, d3) == ("10", "20", "30")


def test_ids_by_names_no_items_key_or_none_items():
    # items キーなし
    d1, d2, d3 = get_departments.get_departments_ids_by_names({}, department_name1="A")
    assert (d1, d2, d3) == (None, None, None)

    # items が None
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        {"items": None}, department_name1="A"
    )
    assert (d1, d2, d3) == (None, None, None)


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


# 追加の網羅テスト（未到達分岐のカバー）


def test_ids_by_names_no_match_with_items():
    # items はあるが、条件に一致する候補がゼロの場合
    result = {"items": [{"departmentName1": "A", "department1": "1"}]}
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="X"  # 一致しない
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_parent_and_grandchild_specified_returns_none():
    # 親と孫のみ指定（子未指定）は仕様外 → 最後のフォールバック (None, None, None)
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
        result, department_name1="A", department_name2=None, department_name3="C"
    )
    assert (d1, d2, d3) == (None, None, None)


def test_ids_by_names_non_string_inputs_and_items():
    # 非文字列（int）を入力・データ側に混在させ、正規化の非文字列分岐をカバー
    result = {
        "items": [
            {"departmentName1": 100, "department1": "X"},
            {"departmentName2": 200, "department2": "Y"},
            {"departmentName3": 300, "department3": "Z"},
        ]
    }
    # 親のみ（int）
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1=100
    )
    assert (d1, d2, d3) == ("X", None, None)
    # 子のみ（int）
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name2=200
    )
    assert (d1, d2, d3) == (None, "Y", None)
    # 孫のみ（int）
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name3=300
    )
    assert (d1, d2, d3) == (None, None, "Z")


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
