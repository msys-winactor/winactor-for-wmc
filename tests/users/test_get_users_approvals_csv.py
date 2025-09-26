import csv
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from winactor_for_wmc.users import get_users_approvals_csv


def test_run_success_with_approvals(mocker):
    """承認待ちスケジュールが存在する場合の正常ケース"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # ユーザー一覧のモックレスポンス
    mock_client.get.side_effect = [
        # 1ページ目のユーザー一覧
        {
            "items": [
                {"id": "user1", "name": "田中太郎"},
                {"id": "user2", "name": "佐藤花子"},
            ]
        },
        # user1の承認待ちスケジュール
        {
            "userPendingApprovalSchedules": [
                {"id": "schedule1", "name": "スケジュール1"},
                {"id": "schedule2", "name": "スケジュール2"},
            ]
        },
        # user2の承認待ちスケジュール
        {
            "userPendingApprovalSchedules": [
                {"id": "schedule3", "name": "スケジュール3"},
            ]
        },
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
        )

    # APIクライアントの呼び出し確認
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")

    # API呼び出し確認
    assert mock_client.get.call_count == 3
    mock_client.get.assert_any_call("/users", params={"page": 1, "size": 100})
    mock_client.get.assert_any_call("/users/user1/approvals")
    mock_client.get.assert_any_call("/users/user2/approvals")

    # ファイル書き込み確認
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="utf-8-sig"
    )

    # 戻り値確認
    assert result is None


def test_run_success_no_approvals(mocker):
    """承認待ちスケジュールが存在しない場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # ユーザー一覧のモックレスポンス
    mock_client.get.side_effect = [
        # ユーザー一覧
        {
            "items": [
                {"id": "user1", "name": "田中太郎"},
            ]
        },
        # user1の承認待ちスケジュール（空）
        {"userPendingApprovalSchedules": []},
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
        )

    # API呼び出し確認
    assert mock_client.get.call_count == 2

    # 戻り値確認
    assert result is None


def test_run_multiple_pages(mocker):
    """複数ページのユーザーが存在する場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # ユーザー一覧のモックレスポンス（2ページ）
    mock_client.get.side_effect = [
        # 1ページ目（100件）
        {"items": [{"id": f"user{i}", "name": f"ユーザー{i}"} for i in range(100)]},
        # 2ページ目（50件）
        {
            "items": [
                {"id": f"user{i}", "name": f"ユーザー{i}"} for i in range(100, 150)
            ]
        },
        # 各ユーザーの承認待ちスケジュール（全て空）
        *[{"userPendingApprovalSchedules": []} for _ in range(150)],
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
        )

    # API呼び出し確認（ユーザー一覧2回 + 各ユーザーの承認待ち150回）
    assert mock_client.get.call_count == 152

    # 戻り値確認
    assert result is None


def test_run_encoding_ms932(mocker):
    """MS932エンコーディングの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.get.side_effect = [
        {"items": [{"id": "user1", "name": "田中太郎"}]},
        {"userPendingApprovalSchedules": []},
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="MS932",
        )

    # Shift_JISエンコーディングでファイルが開かれることを確認
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="shift_jis"
    )


def test_run_user_api_error(mocker, capfd):
    """個別ユーザーのAPI呼び出しでエラーが発生した場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # ユーザー一覧は正常、個別ユーザーでエラー
    mock_client.get.side_effect = [
        {"items": [{"id": "user1", "name": "田中太郎"}]},
        Exception("API Error"),
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
        )

    # エラーが発生しても処理が継続されることを確認
    assert result is None


def test_run_missing_required_params():
    """必須パラメータが不足している場合"""
    with pytest.raises(ValueError, match="base_url, token, file_path は必須です。"):
        get_users_approvals_csv.run()

    with pytest.raises(ValueError, match="base_url, token, file_path は必須です。"):
        get_users_approvals_csv.run(base_url="https://example.com")

    with pytest.raises(ValueError, match="base_url, token, file_path は必須です。"):
        get_users_approvals_csv.run(base_url="https://example.com", token="token")


def test_run_default_encoding(mocker):
    """エンコーディング未指定時のデフォルト値確認"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.get.side_effect = [
        {"items": []},
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            # encoding未指定
        )

    # デフォルトのUTF-8-sigエンコーディングが使用されることを確認
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="utf-8-sig"
    )


def test_run_user_without_id(mocker):
    """ユーザーIDが存在しないユーザーがいる場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # IDがないユーザーを含む
    mock_client.get.side_effect = [
        {
            "items": [
                {"id": "user1", "name": "田中太郎"},
                {"name": "IDなしユーザー"},  # IDがない
                {"id": "user2", "name": "佐藤花子"},
            ]
        },
        # user1の承認待ちスケジュール
        {"userPendingApprovalSchedules": []},
        # user2の承認待ちスケジュール
        {"userPendingApprovalSchedules": []},
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
        )

    # IDがないユーザーはスキップされ、2人のユーザーのみ処理される
    assert mock_client.get.call_count == 3  # ユーザー一覧1回 + 有効ユーザー2回

    assert result is None


def test_run_encoding_unknown(mocker):
    """未知のエンコーディングの場合（elseブロックのテスト）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.users.get_users_approvals_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.get.side_effect = [
        {"items": [{"id": "user1", "name": "田中太郎"}]},
        {"userPendingApprovalSchedules": []},
    ]

    # ファイル書き込みをモック
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_users_approvals_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UNKNOWN_ENCODING",  # 未知のエンコーディング
        )

    # デフォルトのUTF-8-sigエンコーディングが使用されることを確認（elseブロック）
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="utf-8-sig"
    )
