# tests/users/test_delete_users.py
from winactor_for_wmc.users import delete_users


def test_run_calls_delete_by_name(mocker):
    # user_utils.get_user_id_by_name をモック化
    mock_user_utils = mocker.patch("winactor_for_wmc.users.delete_users.user_utils")
    mock_user_utils.get_user_id_by_name.return_value = "user123"

    # WMCApiClient クラスをモック化
    mock_client_class = mocker.patch("winactor_for_wmc.users.delete_users.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.delete.return_value = {"result": "OK"}

    result = delete_users.run(
        base_url="https://example.com",
        token="dummy_token",
        user_name="Taro",
    )

    # user_id 取得が正しく呼ばれること
    mock_user_utils.get_user_id_by_name.assert_called_once_with(
        "https://example.com", "dummy_token", "Taro"
    )

    # クライアント生成とDELETE呼び出しの検証
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.delete.assert_called_once_with("/users/user123")

    # runは何も返していない
    assert result is None
