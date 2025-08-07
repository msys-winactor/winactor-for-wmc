import pytest

from winactor_for_wmc.users import get_users


def test_run_success(mocker):
    # WMCApiClientクラスをモック
    mock_client_class = mocker.patch("winactor_for_wmc.users.get_users.WMCApiClient")
    mock_client = mock_client_class.return_value

    # モックの返すレスポンス（全項目例）
    mock_response = {
        "id": "user123",
        "name": "Test User",
        "department1": 1,
        "department2": 2,
        "department3": 3,
        "departmentName": "本社 営業部 第一課",
        "status": "active",
        "role": "管理者",
        "description": "テストユーザ",
        "autoLogout": 3600,
        "position": "主任",
        "loginFailureCount": 0,
        "loginFailureDate": 0,
        "lastLoginDate": 1753768260071,
        "createdTime": 1753768200000,
        "creatorId": "admin001",
        "updatedTime": 1753768300000,
        "email": "test@example.com",
        "notifyApproval": True,
        "notifyTask": False,
        "notifyWinactor": True,
        "notifyWinactorLimit": False,
        "notifyUndefinedWinactor": False,
        "notifyWinactorLicense": True,
        "notifyTraffic": False,
        "notifyStorage": False,
        "notifyRemainingLicense": True,
        "pageSize": 20,
        "mfa": True,
        "mfaKind": "totp",
        "winactorId": "wa001",
    }
    mock_client.get.return_value = mock_response

    # テスト実行
    base_url = "https://example.com"
    token = "dummy_token"
    user_id = "user123"

    result = get_users.run(base_url=base_url, token=token, user_id=user_id)

    # 検証
    mock_client_class.assert_called_once_with(base_url, token)
    mock_client.get.assert_called_once_with(f"/users/{user_id}")
    assert result == mock_response
