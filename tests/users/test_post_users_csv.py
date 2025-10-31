from unittest.mock import mock_open

import pytest

from winactor_for_wmc.users import post_users_csv


def test_run_with_all_import_data(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success", "processedCount": 10}

    import_data = {"encoding": "UTF-8", "executeType": "I"}
    result = post_users_csv.run(
        base_url="https://example.com",
        token="dummy_token",
        csv_file_path="/path/to/users.csv",
        import_data=import_data,
    )

    client_cls.assert_called_once_with("https://example.com", "dummy_token")
    client.post.assert_called_once()

    call_args = client.post.call_args
    endpoint = call_args.args[0]
    posted_data = call_args.kwargs["data"]
    files = call_args.kwargs["files"]

    assert endpoint == "/users/csv"
    assert posted_data == {"encoding": "UTF-8", "executeType": "I"}
    assert "file" in files
    assert import_data == {
        "encoding": "UTF-8",
        "executeType": "I",
    }  # 呼び出し元は変更されない
    assert result == {"result": "success", "processedCount": 10}


def test_run_with_partial_import_data(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    import_data = {"encoding": "MS932"}
    result = post_users_csv.run(
        base_url="https://example.com",
        token="token123",
        csv_file_path="/path/to/users.csv",
        import_data=import_data,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"encoding": "MS932"}
    assert import_data == {"encoding": "MS932"}  # 呼び出し元は変更されない
    assert result == {"result": "success"}


def test_run_with_only_execute_type(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    import_data = {"executeType": "U"}
    result = post_users_csv.run(
        base_url="https://example.com",
        token="token456",
        csv_file_path="/path/to/users.csv",
        import_data=import_data,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"executeType": "U"}
    assert result == {"result": "success"}


def test_run_with_empty_import_data(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    import_data = {}
    result = post_users_csv.run(
        base_url="https://example.com",
        token="token789",
        csv_file_path="/path/to/users.csv",
        import_data=import_data,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {}
    assert import_data == {}  # 呼び出し元は変更されない
    assert result == {"result": "success"}


def test_run_with_none_import_data(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    result = post_users_csv.run(
        base_url="https://example.com",
        token="token000",
        csv_file_path="/path/to/users.csv",
        import_data=None,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {}
    assert result == {"result": "success"}


def test_run_with_none_base_url_and_token(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    result = post_users_csv.run(
        base_url=None,
        token=None,
        csv_file_path="/path/to/users.csv",
        import_data={"encoding": "UTF-8"},
    )

    client_cls.assert_called_once_with(None, None)
    client.post.assert_called_once()
    assert result == {"result": "success"}


def test_run_with_delete_execute_type(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success", "deletedCount": 5}

    import_data = {"encoding": "MS932", "executeType": "D"}
    result = post_users_csv.run(
        base_url="https://example.com",
        token="delete_token",
        csv_file_path="/path/to/delete_users.csv",
        import_data=import_data,
    )

    client.post.assert_called_once()
    call_args = client.post.call_args
    endpoint = call_args.args[0]
    posted_data = call_args.kwargs["data"]

    assert endpoint == "/users/csv"
    assert posted_data == {"encoding": "MS932", "executeType": "D"}
    assert result == {"result": "success", "deletedCount": 5}


def test_run_file_handling(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(
        read_data=b"userId,userName,email,department\nuser001,John Doe,john@example.com,IT"
    )
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    result = post_users_csv.run(
        base_url="https://example.com",
        token="file_token",
        csv_file_path="/path/to/test.csv",
        import_data={},
    )

    # ファイルが正しく開かれたことを確認
    mock_file.assert_called_once_with("/path/to/test.csv", "rb")

    # filesパラメータにファイルが含まれていることを確認
    files = client.post.call_args.kwargs["files"]
    assert "file" in files

    assert result == {"result": "success"}


def test_run_response_structure_preserved(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    # 複雑なレスポンス構造をテスト
    expected_response = {
        "result": "success",
        "processedCount": 100,
        "errors": [],
        "warnings": ["Warning message"],
        "details": {"created": 50, "updated": 30, "skipped": 20},
    }
    client.post.return_value = expected_response

    result = post_users_csv.run(
        base_url="https://example.com",
        token="complex_token",
        csv_file_path="/path/to/users.csv",
        import_data={"encoding": "UTF-8", "executeType": "I"},
    )

    # レスポンス全体がそのまま返されることを確認
    assert result == expected_response


def test_run_import_data_not_modified_inplace(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success"}

    # 呼び出し元のimport_dataが変更されないことを確認
    original_import_data = {"encoding": "UTF-8", "executeType": "I"}
    import_data = original_import_data.copy()

    result = post_users_csv.run(
        base_url="https://example.com",
        token="immutable_token",
        csv_file_path="/path/to/users.csv",
        import_data=import_data,
    )

    # 呼び出し元のdictが変更されていないことを確認
    assert import_data == original_import_data
    assert result == {"result": "success"}


def test_run_with_update_execute_type(mocker):
    client_cls = mocker.patch("winactor_for_wmc.users.post_users_csv.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"csv content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "success", "updatedCount": 15}

    import_data = {"encoding": "UTF-8", "executeType": "U"}
    result = post_users_csv.run(
        base_url="https://example.com",
        token="update_token",
        csv_file_path="/path/to/update_users.csv",
        import_data=import_data,
    )

    client.post.assert_called_once()
    call_args = client.post.call_args
    endpoint = call_args.args[0]
    posted_data = call_args.kwargs["data"]

    assert endpoint == "/users/csv"
    assert posted_data == {"encoding": "UTF-8", "executeType": "U"}
    assert result == {"result": "success", "updatedCount": 15}
