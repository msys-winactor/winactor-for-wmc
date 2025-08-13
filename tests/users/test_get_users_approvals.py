from copy import deepcopy

import pytest

from winactor_for_wmc.users import get_users_approvals


def test_run_success(mocker):
    # user_utils.get_user_id_by_name をモック
    mock_get_user_id_by_name = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals.user_utils.get_user_id_by_name"
    )
    mock_get_user_id_by_name.return_value = "test_user_id"

    # WMCApiClient をモック
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # モックで返すレスポンス
    mock_response = {
        "userPendingApprovalSchedules": [{"id": "abc", "name": "スケジュール1"}]
    }
    mock_client.get.return_value = mock_response

    # テスト実行
    base_url = "https://example.com"
    token = "dummy_token"
    user_name = "テストユーザー"

    result = get_users_approvals.run(
        base_url=base_url, token=token, user_name=user_name
    )

    # 検証
    mock_get_user_id_by_name.assert_called_once_with(base_url, token, user_name)
    mock_client_class.assert_called_once_with(base_url, token)
    mock_client.get.assert_called_once_with("/users/test_user_id/approvals")
    assert result == mock_response


def test_get_schedule_info_index0():
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, 0)
    assert schedule_id == "abc"
    assert schedule_name == "スケジュール1"


def test_get_schedule_info_index1():
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, 1)
    assert schedule_id == "def"
    assert schedule_name == "スケジュール2"


def test_get_schedule_info_negative_index():
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, -1)
    assert schedule_id == "def"
    assert schedule_name == "スケジュール2"


def test_get_schedule_info_index_as_string():
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, "1")
    assert schedule_id == "def"
    assert schedule_name == "スケジュール2"


@pytest.mark.parametrize("index", [5, -3])
def test_get_schedule_info_out_of_range(index):
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, index)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_schedule_info_empty_list():
    response = {"userPendingApprovalSchedules": []}
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, 0)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_schedule_info_invalid_result_type():
    response = None
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, 0)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_schedule_info_missing_key():
    response = {}  # キーがない場合は空扱い
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, 0)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_schedule_info_missing_fields():
    response = {
        "userPendingApprovalSchedules": [
            {"name": "名前だけ"},  # id なし
            {"id": "only_id"},  # name なし
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, 0)
    assert sid == ""
    assert sname == "名前だけ"

    sid, sname = get_users_approvals.get_schedule_info(response, 1)
    assert sid == "only_id"
    assert sname == ""


# ここから追加分（カバレッジ強化）


@pytest.mark.parametrize("index", ["a", None, "1.0", object()])
def test_get_schedule_info_invalid_index_types(index):
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(response, index)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_schedule_info_index_float_intable():
    # 1.0 -> int 変換成功（正常系）
    response = {
        "userPendingApprovalSchedules": [
            {"id": "a", "name": "x"},
            {"id": "b", "name": "y"},
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, 1.0)
    assert sid == "b" and sname == "y"


def test_get_schedule_info_index_bool():
    # True -> int 変換成功（1）
    response = {
        "userPendingApprovalSchedules": [
            {"id": "a", "name": "x"},
            {"id": "b", "name": "y"},
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, True)
    assert sid == "b" and sname == "y"


def test_get_schedule_info_index_string_with_spaces():
    # " 2 " -> 2 に変換成功
    response = {
        "userPendingApprovalSchedules": [
            {"id": "a", "name": "x"},
            {"id": "b", "name": "y"},
            {"id": "c", "name": "z"},
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, " 2 ")
    assert sid == "c" and sname == "z"


def test_get_schedule_info_index_string_negative():
    # "-1" -> -1 に変換成功（負インデックス）
    response = {
        "userPendingApprovalSchedules": [
            {"id": "a", "name": "x"},
            {"id": "b", "name": "y"},
            {"id": "c", "name": "z"},
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, "-1")
    assert sid == "c" and sname == "z"


@pytest.mark.parametrize("bad_result", ["", 0, 1.5, [], (), set()])
def test_get_schedule_info_non_dict_result(bad_result):
    schedule_id, schedule_name = get_users_approvals.get_schedule_info(bad_result, 0)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_schedule_info_does_not_mutate_input():
    original = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    snapshot = deepcopy(original)

    _ = get_users_approvals.get_schedule_info(original, 1)

    assert original == snapshot


def test_get_schedule_info_large_index_boundary():
    response = {
        "userPendingApprovalSchedules": [
            {"id": str(i), "name": f"スケジュール{i}"} for i in range(5)
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, 4)  # 境界内
    assert sid == "4" and sname == "スケジュール4"

    sid, sname = get_users_approvals.get_schedule_info(response, 5)  # 境界外
    assert sid == "" and sname == ""


def test_get_schedule_info_large_negative_boundary():
    response = {
        "userPendingApprovalSchedules": [
            {"id": str(i), "name": f"スケジュール{i}"} for i in range(5)
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, -5)  # 先頭
    assert sid == "0" and sname == "スケジュール0"

    sid, sname = get_users_approvals.get_schedule_info(response, -6)  # 範囲外
    assert sid == "" and sname == ""


def test_get_schedule_info_partial_fields_and_extra_fields():
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1", "extra": 123},
            {"id": "def"},  # name なし
            {"name": "スケジュール3"},  # id なし
        ]
    }
    sid, sname = get_users_approvals.get_schedule_info(response, 0)
    assert sid == "abc" and sname == "スケジュール1"

    sid, sname = get_users_approvals.get_schedule_info(response, 1)
    assert sid == "def" and sname == ""

    sid, sname = get_users_approvals.get_schedule_info(response, 2)
    assert sid == "" and sname == "スケジュール3"
