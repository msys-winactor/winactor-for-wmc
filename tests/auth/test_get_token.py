"""
get_token.pyのテストファイル
"""

import pytest

from winactor_for_wmc.auth.get_token import get_access_token, run


class TestGetToken:
    """get_tokenモジュールのテストクラス"""

    def test_get_access_token_success(self, mocker):
        """アクセストークン取得の成功テスト"""
        # WMCApiClientのモック
        mock_client = mocker.Mock()
        mock_client.post.return_value = {"token": "test_token_123"}

        mock_client_class = mocker.patch("winactor_for_wmc.auth.get_token.WMCApiClient")
        mock_client_class.return_value = mock_client

        # テスト実行
        result = get_access_token("https://example.com", "test_user", "test_pass")

        # 検証
        assert result == {"token": "test_token_123"}
        mock_client_class.assert_called_once_with("https://example.com", "")
        mock_client.post.assert_called_once_with(
            "/tokens", data={"name": "test_user", "password": "test_pass"}
        )

    def test_get_access_token_no_token_in_response(self, mocker):
        """レスポンスにトークンが含まれない場合のテスト"""
        # WMCApiClientのモック
        mock_client = mocker.Mock()
        mock_client.post.return_value = {"error": "Invalid credentials"}

        mock_client_class = mocker.patch("winactor_for_wmc.auth.get_token.WMCApiClient")
        mock_client_class.return_value = mock_client

        # テスト実行
        result = get_access_token("https://example.com", "test_user", "wrong_pass")

        # 検証
        assert result == {"error": "Invalid credentials"}

    def test_get_access_token_api_error(self, mocker):
        """API呼び出しでエラーが発生した場合のテスト"""
        # WMCApiClientのモック
        mock_client = mocker.Mock()
        mock_client.post.side_effect = RuntimeError(
            "APIエラー (401): 認証に失敗しました"
        )

        mock_client_class = mocker.patch("winactor_for_wmc.auth.get_token.WMCApiClient")
        mock_client_class.return_value = mock_client

        # テスト実行
        with pytest.raises(RuntimeError) as exc_info:
            get_access_token("https://example.com", "test_user", "wrong_pass")

        # 検証
        assert "認証に失敗しました" in str(exc_info.value)

    def test_run_success(self, mocker):
        """run関数の成功テスト"""
        # get_access_tokenのモック
        mock_get_token = mocker.patch(
            "winactor_for_wmc.auth.get_token.get_access_token"
        )
        mock_get_token.return_value = {"token": "success_token_456"}

        # テスト実行
        result = run(
            base_url="https://example.com", user_id="test_user", password="test_pass"
        )

        # 検証 - 現在の実装では辞書全体が返される
        assert result == {"token": "success_token_456"}
        mock_get_token.assert_called_once_with(
            "https://example.com", "test_user", "test_pass"
        )

    def test_run_missing_base_url(self):
        """base_urlが未指定の場合のテスト"""
        with pytest.raises(RuntimeError) as exc_info:
            run(user_id="test_user", password="test_pass")

        assert "ベースURLが指定されていません" in str(exc_info.value)

    def test_run_missing_user_id(self):
        """user_idが未指定の場合のテスト"""
        with pytest.raises(RuntimeError) as exc_info:
            run(base_url="https://example.com", password="test_pass")

        assert "ユーザーIDが指定されていません" in str(exc_info.value)

    def test_run_missing_password(self):
        """passwordが未指定の場合のテスト"""
        with pytest.raises(RuntimeError) as exc_info:
            run(base_url="https://example.com", user_id="test_user")

        assert "パスワードが指定されていません" in str(exc_info.value)

    def test_run_api_error(self, mocker):
        """API呼び出しでエラーが発生した場合のテスト"""
        # get_access_tokenのモック
        mock_get_token = mocker.patch(
            "winactor_for_wmc.auth.get_token.get_access_token"
        )
        mock_get_token.side_effect = RuntimeError("認証に失敗しました")

        # テスト実行
        with pytest.raises(RuntimeError) as exc_info:
            run(
                base_url="https://example.com",
                user_id="test_user",
                password="wrong_pass",
            )

        # 検証
        assert "認証に失敗しました" in str(exc_info.value)

    def test_run_empty_parameters(self):
        """空のパラメータでのテスト"""
        with pytest.raises(RuntimeError) as exc_info:
            run(base_url="", user_id="", password="")

        assert "ベースURLが指定されていません" in str(exc_info.value)

    def test_run_none_parameters(self):
        """Noneパラメータでのテスト"""
        with pytest.raises(RuntimeError) as exc_info:
            run(base_url=None, user_id=None, password=None)

        assert "ベースURLが指定されていません" in str(exc_info.value)
