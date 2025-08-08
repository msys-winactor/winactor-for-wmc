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


def test_get_first_schedule_info_with_schedules():
    response = {
        "userPendingApprovalSchedules": [
            {"id": "abc", "name": "スケジュール1"},
            {"id": "def", "name": "スケジュール2"},
        ]
    }
    schedule_id, schedule_name = get_users_approvals.get_first_schedule_info(response)
    assert schedule_id == "abc"
    assert schedule_name == "スケジュール1"


def test_get_first_schedule_info_empty():
    response = {"userPendingApprovalSchedules": []}
    schedule_id, schedule_name = get_users_approvals.get_first_schedule_info(response)
    assert schedule_id == ""
    assert schedule_name == ""


def test_get_first_schedule_info_invalid_type():
    response = None
    schedule_id, schedule_name = get_users_approvals.get_first_schedule_info(response)
    assert schedule_id == ""
    assert schedule_name == ""
