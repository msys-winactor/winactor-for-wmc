import pytest

from winactor_for_wmc import get_departments


def test_get_departments_success(mocker):
    class MockResponse:
        status_code = 200

        def json(self):
            return {"items": [{"departmentName1": "営業部", "department1": 1}]}

    mocker.patch(
        "winactor_for_wmc.get_departments.requests.get", return_value=MockResponse()
    )
    res = get_departments.get_departments("http://dummy", "token")
    assert res == {"items": [{"departmentName1": "営業部", "department1": 1}]}


def test_get_departments_api_error(mocker):
    class MockResponse:
        status_code = 400

        def json(self):
            return {"error": "Bad", "detail": "詳細"}

    mocker.patch(
        "winactor_for_wmc.get_departments.requests.get", return_value=MockResponse()
    )
    with pytest.raises(get_departments.GetDepartmentsError) as excinfo:
        get_departments.get_departments("http://dummy", "token")
    assert "status_code: 400" in str(excinfo.value)


def test_get_departments_requests_exception(mocker):
    mocker.patch(
        "winactor_for_wmc.get_departments.requests.get",
        side_effect=Exception("network error"),
    )
    with pytest.raises(get_departments.GetDepartmentsError) as excinfo:
        get_departments.get_departments("http://dummy", "token")
    assert "network error" in str(excinfo.value)


def test_get_departments_json_decode_error(mocker):
    class MockResponse:
        status_code = 400

        def json(self):
            raise Exception("json decode error")

    mocker.patch(
        "winactor_for_wmc.get_departments.requests.get", return_value=MockResponse()
    )
    with pytest.raises(get_departments.GetDepartmentsError) as excinfo:
        get_departments.get_departments("http://dummy", "token")
    assert "json decode error" in str(excinfo.value)


def test_get_departments_error_reraise(mocker):
    def raise_get_dept_error(*args, **kwargs):
        raise get_departments.GetDepartmentsError("already error")

    mocker.patch(
        "winactor_for_wmc.get_departments.requests.get",
        side_effect=raise_get_dept_error,
    )
    with pytest.raises(get_departments.GetDepartmentsError) as excinfo:
        get_departments.get_departments("http://dummy", "token")
    assert "already error" in str(excinfo.value)


def test_get_departments_all_params(mocker):
    class MockResponse:
        status_code = 200

        def json(self):
            return {"items": []}

    mock = mocker.patch(
        "winactor_for_wmc.get_departments.requests.get", return_value=MockResponse()
    )
    res = get_departments.get_departments(
        "http://dummy",
        "token",
        idType="abc",
        id="123",
        department1="d1",
        department2="d2",
        department3="d3",
        page=0,
        size=10,
    )
    assert res == {"items": []}
    assert mock.call_args[1]["params"] == {
        "idType": "abc",
        "id": "123",
        "department1": "d1",
        "department2": "d2",
        "department3": "d3",
        "page": 0,
        "size": 10,
    }


def test_get_departments_no_params(mocker):
    class MockResponse:
        status_code = 200

        def json(self):
            return {"items": []}

    mock = mocker.patch(
        "winactor_for_wmc.get_departments.requests.get", return_value=MockResponse()
    )
    res = get_departments.get_departments("http://dummy", "token")
    assert res == {"items": []}
    assert mock.call_args[1]["params"] == {}


def test_get_department_ids_by_names_all_match():
    result = {
        "items": [
            {
                "departmentName1": "営業部",
                "department1": 1,
                "departmentName2": "東日本",
                "department2": 2,
                "departmentName3": "A班",
                "department3": 3,
            },
            {
                "departmentName1": "開発部",
                "department1": 4,
            },
        ]
    }
    d1, d2, d3 = get_departments.get_department_ids_by_names(
        result,
        department_name1="営業部",
        department_name2="東日本",
        department_name3="A班",
    )
    assert d1 == 1
    assert d2 == 2
    assert d3 == 3


def test_get_department_ids_by_names_partial_match():
    result = {"items": [{"departmentName1": "営業部", "department1": 1}]}
    d1, d2, d3 = get_departments.get_department_ids_by_names(
        result, department_name1="営業部", department_name2="東日本"
    )
    assert d1 == 1
    assert d2 is None
    assert d3 is None


def test_get_department_ids_by_names_no_match():
    result = {"items": [{"departmentName1": "営業部", "department1": 1}]}
    d1, d2, d3 = get_departments.get_department_ids_by_names(
        result, department_name1="不存在"
    )
    assert d1 is None and d2 is None and d3 is None
