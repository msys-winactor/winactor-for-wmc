# tests/users/test_post_users.py

import pytest

from winactor_for_wmc.users import post_users


def test_run_all_departments(mocker):
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", "2", "3")
    client.post.return_value = {"result": "OK"}

    user_data = {}
    result = post_users.run(
        base_url="https://example.com",
        token="dummy",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3="C",
    )

    gd.get_departments.assert_called_once_with(
        base_url="https://example.com", token="dummy"
    )
    gd.get_departments.get_departments_ids_by_names.assert_not_called()  # 直接は呼ばれない
    gd.get_departments_ids_by_names.assert_called_once()  # 属性経由での呼び出しを検証
    client_cls.assert_called_once_with("https://example.com", "dummy")
    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department1": "1", "department2": "2", "department3": "3"}
    # 呼び出し元の空 dict は or {} により変更されない
    assert user_data == {}
    assert result == {"result": "OK"}


def test_run_partial_departments_only_parent(mocker):
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = ("1", None, None)
    client.post.return_value = {"result": "OK"}

    user_data = {}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1="A",
        department_name2=None,
        department_name3=None,
    )

    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department1": "1"}
    assert user_data == {}  # in-place 更新なし
    assert result == {"result": "OK"}


def test_run_only_department2(mocker):
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "2", None)
    client.post.return_value = {"result": "OK"}

    user_data = {}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1=None,
        department_name2="B",
        department_name3=None,
    )

    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department2": "2"}
    assert user_data == {}  # in-place 更新なし
    assert result == {"result": "OK"}


def test_run_only_department3(mocker):
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, "3")
    client.post.return_value = {"result": "OK"}

    user_data = {}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1=None,
        department_name2=None,
        department_name3="C",
    )

    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department3": "3"}
    assert user_data == {}  # in-place 更新なし
    assert result == {"result": "OK"}


def test_run_no_departments_defaults_added(mocker):
    # 3つとも falsy → 既定値を付与。ただし呼び出し側 user_data は空 dict なので in-place 反映されない
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value
    client.post.return_value = {"result": "OK"}

    user_data = {}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    gd.get_departments.assert_not_called()
    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department1": 0, "department2": None, "department3": None}
    assert user_data == {}  # or {} により別インスタンス使用のため変更されない
    assert result == {"result": "OK"}


def test_run_none_user_data_defaults_added(mocker):
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value
    client.post.return_value = {"result": "OK"}

    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=None,
        department_name1=None,
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_not_called()
    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department1": 0, "department2": None, "department3": None}
    assert result == {"result": "OK"}


def test_run_with_department_names_but_no_match_adds_nothing(mocker):
    # 指定はあるが、ID 解決が全て None → 追加なし
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.post.return_value = {"result": "OK"}

    user_data = {"loginId": "u001"}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"loginId": "u001"}
    assert user_data == {"loginId": "u001"}
    assert result == {"result": "OK"}


def test_run_whitespace_name_triggers_lookup_but_adds_nothing(mocker):
    # スペースのみは truthy → ルックアップは実施されるが、None が返れば追加されない
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, None, None)
    client.post.return_value = {"result": "OK"}

    user_data = {"loginId": "u002"}
    result = post_users.run(
        base_url=None,  # None でもクライアント生成される
        token="t",
        user_data=user_data,
        department_name1="   ",  # truthy
        department_name2=None,
        department_name3=None,
    )

    gd.get_departments.assert_called_once_with(base_url=None, token="t")
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"loginId": "u002"}
    assert result == {"result": "OK"}


def test_run_ids_zero_and_empty_string_are_posted(mocker):
    # 0 と "" は None ではない → 追加される。ただし呼び出し側の空 dict は変更されない
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (0, "", None)
    client.post.return_value = {"result": "OK"}

    user_data = {}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department1": 0, "department2": ""}
    assert user_data == {}  # 空 dict のため in-place 反映されない
    assert result == {"result": "OK"}


def test_run_overwrites_existing_department_fields(mocker):
    # 既存の値は新しい ID で上書き（None はスキップ）。呼び出し側が truthy dict のため in-place 反映される
    gd = mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value

    gd.get_departments.return_value = {"items": []}
    gd.get_departments_ids_by_names.return_value = (None, "22", None)
    client.post.return_value = {"result": "OK"}

    user_data = {"department1": "old1", "department2": "old2", "extra": "keep"}
    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1="A",
        department_name2="B",
        department_name3=None,
    )

    posted = client.post.call_args.kwargs["data"]
    assert posted == {"department1": "old1", "department2": "22", "extra": "keep"}
    assert user_data == {"department1": "old1", "department2": "22", "extra": "keep"}
    assert result == {"result": "OK"}


def test_run_no_departments_with_non_empty_user_data_inplace_update(mocker):
    # 3つとも falsy ＋ user_data が非空 dict → 既定値が in-place で追加されるブランチ
    mocker.patch("winactor_for_wmc.users.post_users.get_departments")
    client_cls = mocker.patch("winactor_for_wmc.users.post_users.WMCApiClient")
    client = client_cls.return_value
    client.post.return_value = {"result": "OK"}

    user_data = {"extra": "keep"}  # 非空で渡す

    result = post_users.run(
        base_url="https://example.com",
        token="t",
        user_data=user_data,
        department_name1=None,
        department_name2="",
        department_name3="",
    )

    client.post.assert_called_once()
    posted = client.post.call_args.kwargs["data"]
    assert posted == {
        "extra": "keep",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    # in-place 反映されることを確認
    assert user_data == {
        "extra": "keep",
        "department1": 0,
        "department2": None,
        "department3": None,
    }
    assert result == {"result": "OK"}
