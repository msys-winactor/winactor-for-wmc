import pytest

from winactor_for_wmc.users import get_users


def test_run_success(mocker):
    # user_utils.get_user_id_by_name をモック
    mock_get_user_id_by_name = mocker.patch(
        "winactor_for_wmc.common.user_utils.get_user_id_by_name"
    )
    mock_get_user_id_by_name.return_value = "user123"

    # WMCApiClient をモック
    mock_client_class = mocker.patch("winactor_for_wmc.users.get_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    mock_response = {"id": "user123", "name": "Test User"}
    mock_client.get.return_value = mock_response

    # テスト用パラメータ
    base_url = "https://example.com"
    token = "dummy_token"
    user_name = "テストユーザー"

    # テスト実行
    result = get_users.run(base_url=base_url, token=token, user_name=user_name)

    # アサーション
    mock_get_user_id_by_name.assert_called_once_with(base_url, token, user_name)
    mock_client_class.assert_called_once_with(base_url, token)
    mock_client.get.assert_called_once_with("/users/user123")
    assert result == mock_response
