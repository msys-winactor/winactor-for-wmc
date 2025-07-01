import pytest

from winactor_for_wmc import post_files


def setup_common_mocks(mocker, dept_ids=(1, 2, 3)):
    # get_departments.get_departments のモック
    mocker.patch(
        "winactor_for_wmc.post_files.get_departments.get_departments",
        return_value={
            "items": [
                {
                    "departmentName1": "営業部",
                    "department1": 1,
                    "departmentName2": "東日本",
                    "department2": 2,
                    "departmentName3": "A班",
                    "department3": 3,
                }
            ]
        },
    )
    # get_departments.get_department_ids_by_names のモック
    mocker.patch(
        "winactor_for_wmc.post_files.get_departments.get_department_ids_by_names",
        return_value=dept_ids,
    )


def test_upload_file_with_department_names_success(mocker, tmp_path):
    setup_common_mocks(mocker)
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "file123"}

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post",
        return_value=MockResponse(),
    )
    result = post_files.upload_file_with_department_names(
        "http://dummy/files",
        "http://dummy/departments",
        "token",
        str(test_file),
        {"autoDeleteFlag": "true", "fileTag": "UMS"},
        department_name1="営業部",
        department_name2="東日本",
        department_name3="A班",
    )
    assert result == "file123"


def test_upload_file_with_department_names_api_error_json(mocker, tmp_path):
    setup_common_mocks(mocker)
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 400

        def json(self):
            return {"error": "Bad", "detail": "詳細"}

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post",
        return_value=MockResponse(),
    )
    with pytest.raises(post_files.UploadFileError) as excinfo:
        post_files.upload_file_with_department_names(
            "http://dummy/files",
            "http://dummy/departments",
            "token",
            str(test_file),
            {"autoDeleteFlag": "true"},
            department_name1="営業部",
        )
    assert "status_code: 400" in str(excinfo.value)
    assert "Bad" in str(excinfo.value)


def test_upload_file_with_department_names_api_error_json_decode(mocker, tmp_path):
    setup_common_mocks(mocker)
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 400

        def json(self):
            raise Exception("json decode error")

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post",
        return_value=MockResponse(),
    )
    with pytest.raises(post_files.UploadFileError) as excinfo:
        post_files.upload_file_with_department_names(
            "http://dummy/files",
            "http://dummy/departments",
            "token",
            str(test_file),
            {"autoDeleteFlag": "true"},
            department_name1="営業部",
        )
    assert "status_code: 400" in str(excinfo.value)


def test_upload_file_with_department_names_post_exception(mocker, tmp_path):
    setup_common_mocks(mocker)
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post",
        side_effect=Exception("post error"),
    )
    with pytest.raises(post_files.UploadFileError) as excinfo:
        post_files.upload_file_with_department_names(
            "http://dummy/files",
            "http://dummy/departments",
            "token",
            str(test_file),
            {"autoDeleteFlag": "true"},
            department_name1="営業部",
        )
    assert "post error" in str(excinfo.value)


def test_upload_file_with_department_names_get_departments_error(mocker, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")
    mocker.patch(
        "winactor_for_wmc.post_files.get_departments.get_departments",
        side_effect=post_files.get_departments.GetDepartmentsError("部門取得エラー"),
    )
    with pytest.raises(post_files.UploadFileError) as excinfo:
        post_files.upload_file_with_department_names(
            "http://dummy/files",
            "http://dummy/departments",
            "token",
            str(test_file),
            {"autoDeleteFlag": "true"},
            department_name1="営業部",
        )
    assert "部門取得エラー" in str(excinfo.value)


# --- ここから分岐網羅テスト ---


def test_upload_file_with_only_department1(mocker, tmp_path):
    setup_common_mocks(mocker, dept_ids=(1, None, None))
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "file1"}

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post", return_value=MockResponse()
    )
    result = post_files.upload_file_with_department_names(
        "http://dummy/files",
        "http://dummy/departments",
        "token",
        str(test_file),
        {"autoDeleteFlag": "true"},
        department_name1="営業部",
    )
    assert result == "file1"


def test_upload_file_with_only_department2(mocker, tmp_path):
    setup_common_mocks(mocker, dept_ids=(None, 2, None))
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "file2"}

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post", return_value=MockResponse()
    )
    result = post_files.upload_file_with_department_names(
        "http://dummy/files",
        "http://dummy/departments",
        "token",
        str(test_file),
        {"autoDeleteFlag": "true"},
        department_name2="東日本",
    )
    assert result == "file2"


def test_upload_file_with_only_department3(mocker, tmp_path):
    setup_common_mocks(mocker, dept_ids=(None, None, 3))
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "file3"}

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post", return_value=MockResponse()
    )
    result = post_files.upload_file_with_department_names(
        "http://dummy/files",
        "http://dummy/departments",
        "token",
        str(test_file),
        {"autoDeleteFlag": "true"},
        department_name3="A班",
    )
    assert result == "file3"


def test_upload_file_with_no_departments(mocker, tmp_path):
    setup_common_mocks(mocker, dept_ids=(None, None, None))
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"test")

    class MockResponse:
        status_code = 201

        def json(self):
            return {"id": "file0"}

    mocker.patch(
        "winactor_for_wmc.post_files.requests.post", return_value=MockResponse()
    )
    result = post_files.upload_file_with_department_names(
        "http://dummy/files",
        "http://dummy/departments",
        "token",
        str(test_file),
        {"autoDeleteFlag": "true"},
    )
    assert result == "file0"
