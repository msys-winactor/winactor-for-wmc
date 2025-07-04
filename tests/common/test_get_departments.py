import pytest

from winactor_for_wmc.common import get_departments


def test_get_departments_all_params(mocker):
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


def test_get_departments_partial_params(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.common.get_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"items": []}

    result = get_departments.get_departments(
        base_url="https://example.com", token="dummy", department1="1"
    )
    called_params = mock_client.get.call_args[1]["params"]
    assert called_params["department1"] == "1"
    assert "department2" not in called_params
    assert "department3" not in called_params
    assert "idType" not in called_params
    assert "id" not in called_params
    assert "page" not in called_params
    assert "size" not in called_params


def test_get_departments_base_url_none():
    # base_urlがNoneの場合
    with pytest.raises(AttributeError):
        get_departments.get_departments(base_url=None, token="dummy")


def test_get_departments_ids_by_names_all_match():
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
    assert d1 == "1"
    assert d2 == "2"
    assert d3 == "3"


def test_get_departments_ids_by_names_partial_and_empty():
    # itemsが空
    result = {"items": []}
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="X"
    )
    assert d1 is None and d2 is None and d3 is None

    # itemsに一致しない
    result = {"items": [{"departmentName1": "Y", "department1": "9"}]}
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="X"
    )
    assert d1 is None and d2 is None and d3 is None

    # どれかだけ一致
    result = {"items": [{"departmentName1": "A", "department1": "1"}]}
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A", department_name2="B"
    )
    assert d1 == "1" and d2 is None and d3 is None


def test_get_departments_ids_by_names_no_items_key():
    # itemsキーがない場合
    result = {}
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A"
    )
    assert d1 is None and d2 is None and d3 is None


def test_get_departments_ids_by_names_items_is_none():
    # itemsがNoneの場合
    result = {"items": None}
    d1, d2, d3 = get_departments.get_departments_ids_by_names(
        result, department_name1="A"
    )
    assert d1 is None and d2 is None and d3 is None


def test_get_departments_ids_by_names_all_none_params():
    # department_name1, department_name2, department_name3 が全てNoneの場合
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
    assert d1 is None and d2 is None and d3 is None


def test_get_departments_ids_by_names_multiple_items():
    # 複数itemsがあっても最初に一致したものを返す
    result = {
        "items": [
            {
                "departmentName1": "X",
                "department1": "9",
                "departmentName2": "Y",
                "department2": "8",
                "departmentName3": "Z",
                "department3": "7",
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
    assert d1 == "1" and d2 == "2" and d3 == "3"
