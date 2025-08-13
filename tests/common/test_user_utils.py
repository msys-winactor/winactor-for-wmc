import pytest

from winactor_for_wmc.common import user_utils


def test_get_user_id_by_name(mocker):
    mock_client_class = mocker.patch("winactor_for_wmc.common.user_utils.WMCApiClient")
    mock_client = mock_client_class.return_value

    # モックレスポンス
    mock_response = {"items": [{"id": "user123"}]}
    mock_client.get.return_value = mock_response

    base_url = "https://example.com"
    token = "dummy_token"
    user_name = "テストユーザー"

    user_id = user_utils.get_user_id_by_name(base_url, token, user_name)

    mock_client_class.assert_called_once_with(base_url, token)
    mock_client.get.assert_called_once_with(
        "/users", params={"name": user_name, "nameType": "perfect", "size": 1}
    )
    assert user_id == "user123"
