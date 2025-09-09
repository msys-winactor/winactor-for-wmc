# tests/users/test_put_users.py

import pytest

from winactor_for_wmc.users import put_users


def test_run_all_departments(mocker):
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user123"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", "2", "3")
    client.put.return_value = {"result": "OK"}

    user_data = {"existing": "data"}  # 非空辞書を使用
    result = put_users.run(
        base_url="https://example.com",
        token="dummy",
        user_name="test_user",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    user_utils.get_user_id_by_name.assert_called_once_with(
        "https://example.com", "dummy", "test_user"
    )
    gd.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy"
    )
    gd.get_departments_ids_by_names.assert_called_once()
    client_cls.assert_called_once_with("https://example.com", "dummy")
    client.put.assert_called_once_with(
        "/users/user123",
        data={
            "existing": "data",
            "department1": "1",
            "department2": "2",
            "department3": "3",
        },
    )
    assert user_data == {
        "existing": "data",
        "department1": "1",
        "department2": "2",
        "department3": "3",
    }
    assert result == {"result": "OK"}


def test_run_partial_departments_only_parent(mocker):
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user456"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", None, None)
    client.put.return_value = {"result": "OK"}

    user_data = {"existing": "data"}  # 非空辞書を使用
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    client.put.assert_called_once_with(
        "/users/user456", data={"existing": "data", "department1": "1"}
    )
    assert user_data == {"existing": "data", "department1": "1"}
    assert result == {"result": "OK"}


def test_run_only_department2(mocker):
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user789"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "2", None)
    client.put.return_value = {"result": "OK"}

    user_data = {"existing": "data"}  # 非空辞書を使用
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1=None,
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once_with(
        "/users/user789", data={"existing": "data", "department2": "2"}
    )
    assert user_data == {"existing": "data", "department2": "2"}
    assert result == {"result": "OK"}


def test_run_only_department3(mocker):
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user101"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, "3")
    client.put.return_value = {"result": "OK"}

    user_data = {"existing": "data"}  # 非空辞書を使用
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1=None,
        department_name2=None,
        department_name3="C",
    )

    client.put.assert_called_once_with(
        "/users/user101", data={"existing": "data", "department3": "3"}
    )
    assert user_data == {"existing": "data", "department3": "3"}
    assert result == {"result": "OK"}


def test_run_no_departments_defaults_added(mocker):
    # 3つとも falsy → 既定値を付与（未所属にリセット）
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user202"
    client.put.return_value = {"result": "OK"}

    user_data = {"existing": "data"}  # 非空辞書を使用
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    gd.get_departments.assert_not_called()
    client.put.assert_called_once_with(
        "/users/user202",
        data={
            "existing": "data",
            "department1": 0,
            "department2": None,
            "department3": None,
        },
    )
    assert user_data == {
        "existing": "data",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    assert result == {"result": "OK"}


def test_run_none_user_data_defaults_added(mocker):
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user303"
    client.put.return_value = {"result": "OK"}

    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_not_called()
    client.put.assert_called_once_with(
        "/users/user303",
        data={"department1": 0, "department2": None, "department3": None},
    )
    assert result == {"result": "OK"}


def test_run_with_department_names_but_no_match_adds_nothing(mocker):
    # 指定はあるが、ID 解決が全て None → 追加なし
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user404"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.put.return_value = {"result": "OK"}

    user_data = {"loginId": "u001"}
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once_with("/users/user404", data={"loginId": "u001"})
    assert user_data == {"loginId": "u001"}
    assert result == {"result": "OK"}


def test_run_whitespace_name_triggers_lookup_but_adds_nothing(mocker):
    # スペースのみは truthy → ルックアップは実施されるが、None が返れば追加されない
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user505"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.put.return_value = {"result": "OK"}

    user_data = {"loginId": "u002"}
    result = put_users.run(
        base_url=None,  # None でもクライアント生成される
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1="   ",  # truthy
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_called_once_with(base_url=None, token="t")
    client.put.assert_called_once_with("/users/user505", data={"loginId": "u002"})
    assert result == {"result": "OK"}


def test_run_ids_zero_and_empty_string_are_posted(mocker):
    # 0 と "" は None ではない → 追加される
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user606"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (0, "", None)
    client.put.return_value = {"result": "OK"}

    user_data = {"existing": "data"}  # 非空辞書を使用
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once_with(
        "/users/user606", data={"existing": "data", "department1": 0, "department2": ""}
    )
    assert user_data == {"existing": "data", "department1": 0, "department2": ""}
    assert result == {"result": "OK"}


def test_run_overwrites_existing_department_fields(mocker):
    # 既存の値は新しい ID で上書き（None はスキップ）
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user707"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "22", None)
    client.put.return_value = {"result": "OK"}

    user_data = {"department1": "old1", "department2": "old2", "extra": "keep"}
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.put.assert_called_once_with(
        "/users/user707",
        data={"department1": "old1", "department2": "22", "extra": "keep"},
    )
    assert user_data == {"department1": "old1", "department2": "22", "extra": "keep"}
    assert result == {"result": "OK"}


def test_run_no_departments_with_non_empty_user_data_inplace_update(mocker):
    # 3つとも falsy ＋ user_data が非空 dict → 既定値が in-place で追加される
    mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user808"
    client.put.return_value = {"result": "OK"}

    user_data = {"extra": "keep"}  # 非空で渡す

    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    client.put.assert_called_once_with(
        "/users/user808",
        data={
            "extra": "keep",
            "department1": 0,
            "department2": None,
            "department3": None,
        },
    )
    # in-place 反映されることを確認
    assert user_data == {
        "extra": "keep",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    assert result == {"result": "OK"}


def test_run_empty_user_data_not_modified_inplace(mocker):
    # 空辞書の場合、in-place修正されない（`user_data or {}`の動作確認）
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "user909"
    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", "2", "3")
    client.put.return_value = {"result": "OK"}

    user_data = {}  # 空辞書
    result = put_users.run(
        base_url="https://example.com",
        token="t",
        user_name="test_user",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    # 空辞書は`user_data or {}`により新しい辞書が使われるため、元は変更されない
    client.put.assert_called_once_with(
        "/users/user909",
        data={"department1": "1", "department2": "2", "department3": "3"},
    )
    assert user_data == {}  # 元の空辞書は変更されない
    assert result == {"result": "OK"}


def test_run_missing_user_name_raises_error():
    # user_name が空の場合は ValueError
    with pytest.raises(ValueError, match="user_name is required"):
        put_users.run(
            base_url="https://example.com",
            token="t",
            user_name=None,
            user_data={},
        )

    with pytest.raises(ValueError, match="user_name is required"):
        put_users.run(
            base_url="https://example.com",
            token="t",
            user_name="",
            user_data={},
        )


def test_run_user_id_lookup_called_correctly(mocker):
    # user_utils.get_user_id_by_name の呼び出しを詳細に検証
    gd = mocker.patch("winactor_for_wmc.users.put_users.get_departments")
    user_utils = mocker.patch("winactor_for_wmc.users.put_users.user_utils")
    client_cls = mocker.patch("winactor_for_wmc.users.put_users.WMCApiClient")
    client = client_cls.return_value

    user_utils.get_user_id_by_name.return_value = "found_user_id"
    client.put.return_value = {}

    result = put_users.run(
        base_url="https://test.example.com",
        token="test_token",
        user_name="target_user",
        user_data={"field": "value"},
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    user_utils.get_user_id_by_name.assert_called_once_with(
        "https://test.example.com", "test_token", "target_user"
    )
    client.put.assert_called_once_with(
        "/users/found_user_id",
        data={
            "field": "value",
            "department1": 0,
            "department2": None,
            "department3": None,
        },
    )
