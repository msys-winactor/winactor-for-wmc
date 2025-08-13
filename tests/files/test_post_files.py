import pytest

from winactor_for_wmc.files import post_files


def test_run_all_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.files.post_files.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 部門取得
    mock_get_departments.get_departments.return_value = {
        "items": [
            {"departmentName1": "A", "department1": "1"},
            {"departmentName2": "B", "department2": "2"},
            {"departmentName3": "C", "department3": "3"},
        ]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", "2", "3")
    mock_client.post.return_value = {"id": "file_id_123"}

    file_data = {}
    # openのモック
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"dummy"))

    file_id = post_files.run(
        base_url="https://example.com",
        token="dummy_token",
        file_path="dummy.txt",
        file_data=file_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    mock_get_departments.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy_token"
    )
    mock_get_departments.get_departments_ids_by_names.assert_called_once()
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.post.assert_called_once()
    assert file_data["department1"] == "1"
    assert file_data["department2"] == "2"
    assert file_data["department3"] == "3"
    assert file_id == "file_id_123"


def test_run_partial_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.files.post_files.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {
        "items": [{"departmentName1": "A", "department1": "1"}]
    }
    mock_get_departments.get_departments_ids_by_names.return_value = ("1", None, None)
    mock_client.post.return_value = {"id": "file_id_456"}
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"dummy"))

    file_data = {}
    file_id = post_files.run(
        base_url="https://example.com",
        token="dummy_token",
        file_path="dummy.txt",
        file_data=file_data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )
    assert file_data["department1"] == "1"
    assert "department2" not in file_data
    assert "department3" not in file_data
    assert file_id == "file_id_456"


def test_run_no_departments(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.files.post_files.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)
    mock_client.post.return_value = {"id": "file_id_789"}
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"dummy"))

    file_data = {}
    file_id = post_files.run(
        base_url="https://example.com",
        token="dummy_token",
        file_path="dummy.txt",
        file_data=file_data,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )
    assert "department1" not in file_data
    assert "department2" not in file_data
    assert "department3" not in file_data
    assert file_id == "file_id_789"


def test_run_api_error(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.files.post_files.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 部門取得は正常
    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)

    # APIがエラーを返す
    mock_client.post.return_value = {}  # idがないパターン

    mocker.patch("builtins.open", mocker.mock_open(read_data=b"dummy"))

    file_data = {}
    file_id = post_files.run(
        base_url="https://example.com",
        token="dummy_token",
        file_path="dummy.txt",
        file_data=file_data,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )
    # idがない場合はNoneが返る想定
    assert file_id is None


def test_run_file_open_error(mocker):
    mock_get_departments = mocker.patch(
        "winactor_for_wmc.files.post_files.get_departments"
    )
    mock_client_class = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    mock_client = mock_client_class.return_value

    # 部門取得は正常
    mock_get_departments.get_departments.return_value = {"items": []}
    mock_get_departments.get_departments_ids_by_names.return_value = (None, None, None)

    # ファイルが開けない場合（例外発生）
    mocker.patch("builtins.open", side_effect=FileNotFoundError("not found"))

    file_data = {}
    with pytest.raises(FileNotFoundError):
        post_files.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="dummy.txt",
            file_data=file_data,
            department_name1=None,
            department_name2=None,
            department_name3=None,
        )
