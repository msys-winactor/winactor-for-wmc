from unittest.mock import mock_open

import pytest

from winactor_for_wmc.files import post_files


def test_run_all_departments(mocker):
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", "2", "3")
    client.post.return_value = {"id": "file123"}

    file_data = {}
    result = post_files.run(
        base_url="https://example.com",
        token="dummy",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    gd.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy"
    )
    gd.get_departments_ids_by_names.assert_called_once()
    client_cls.assert_called_once_with("https://example.com", "dummy")
    client.post.assert_called_once()

    call_args = client.post.call_args
    posted_data = call_args.kwargs["data"]
    files = call_args.kwargs["files"]

    assert posted_data == {"department1": "1", "department2": "2", "department3": "3"}
    assert "file" in files
    assert file_data == {}  # 呼び出し元の空 dict は or {} により変更されない
    assert result == "file123"


def test_run_partial_departments_only_parent(mocker):
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", None, None)
    client.post.return_value = {"id": "file456"}

    file_data = {}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"department1": "1"}
    assert file_data == {}  # in-place 更新なし
    assert result == "file456"


def test_run_only_department2(mocker):
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "2", None)
    client.post.return_value = {"id": "file789"}

    file_data = {}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1=None,
        department_name2="B",
        department_name3=None,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"department2": "2"}
    assert file_data == {}  # in-place 更新なし
    assert result == "file789"


def test_run_only_department3(mocker):
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, "3")
    client.post.return_value = {"id": "file999"}

    file_data = {}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1=None,
        department_name2=None,
        department_name3="C",
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"department3": "3"}
    assert file_data == {}  # in-place 更新なし
    assert result == "file999"


def test_run_no_departments_defaults_added(mocker):
    # 3つとも falsy → 既定値を付与。ただし呼び出し側 file_data は空 dict なので in-place 反映されない
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"id": "default_file"}

    file_data = {}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    gd.get_departments.assert_not_called()
    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"department1": 0, "department2": None, "department3": None}
    assert file_data == {}  # or {} により別インスタンス使用のため変更されない
    assert result == "default_file"


def test_run_none_file_data_defaults_added(mocker):
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"id": "none_file"}

    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_not_called()
    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"department1": 0, "department2": None, "department3": None}
    assert result == "none_file"


def test_run_with_department_names_but_no_match_adds_nothing(mocker):
    # 指定はあるが、ID 解決が全て None → 追加なし
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.post.return_value = {"id": "no_match_file"}

    file_data = {"filename": "test.txt"}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"filename": "test.txt"}
    assert file_data == {"filename": "test.txt"}
    assert result == "no_match_file"


def test_run_whitespace_name_triggers_lookup_but_adds_nothing(mocker):
    # スペースのみは truthy → ルックアップは実施されるが、None が返れば追加されない
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.post.return_value = {"id": "whitespace_file"}

    file_data = {"filename": "test2.txt"}
    result = post_files.run(
        base_url=None,  # None でもクライアント生成される
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1="   ",  # truthy
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_called_once_with(base_url=None, token="t")
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"filename": "test2.txt"}
    assert result == "whitespace_file"


def test_run_ids_zero_and_empty_string_are_posted(mocker):
    # 0 と "" は None ではない → 追加される。ただし呼び出し側の空 dict は変更されない
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (0, "", None)
    client.post.return_value = {"id": "zero_empty_file"}

    file_data = {}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {"department1": 0, "department2": ""}
    assert file_data == {}  # 空 dict のため in-place 反映されない
    assert result == "zero_empty_file"


def test_run_overwrites_existing_department_fields(mocker):
    # 既存の値は新しい ID で上書き（None はスキップ）。呼び出し側が truthy dict のため in-place 反映される
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "22", None)
    client.post.return_value = {"id": "overwrite_file"}

    file_data = {"department1": "old1", "department2": "old2", "filename": "keep.txt"}
    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {
        "department1": "old1",
        "department2": "22",
        "filename": "keep.txt",
    }
    assert file_data == {
        "department1": "old1",
        "department2": "22",
        "filename": "keep.txt",
    }
    assert result == "overwrite_file"


def test_run_no_departments_with_non_empty_file_data_inplace_update(mocker):
    # 3つとも falsy ＋ file_data が非空 dict → 既定値が in-place で追加されるブランチ
    mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"id": "inplace_file"}

    file_data = {"filename": "keep.txt"}  # 非空で渡す

    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data=file_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    client.post.assert_called_once()
    posted_data = client.post.call_args.kwargs["data"]
    assert posted_data == {
        "filename": "keep.txt",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    # in-place 反映されることを確認
    assert file_data == {
        "filename": "keep.txt",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    assert result == "inplace_file"


def test_run_response_without_id_returns_none(mocker):
    # response に id がない場合は None が返される
    gd = mocker.patch("winactor_for_wmc.files.post_files.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.files.post_files.WMCApiClient")
    client = client_cls.return_value
    mock_file = mock_open(read_data=b"file content")
    mocker.patch("builtins.open", mock_file)

    client.post.return_value = {"result": "OK"}  # id フィールドなし

    result = post_files.run(
        base_url="https://example.com",
        token="t",
        file_path="/path/to/file.txt",
        file_data={},
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    assert result is None
