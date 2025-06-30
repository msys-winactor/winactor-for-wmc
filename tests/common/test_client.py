import json

import pytest
import requests

from winactor_for_wmc.common.client import WMCApiClient


class TestWMCApiClient:
    """WMCApiClientのテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化"""
        self.base_url = "https://example.com"
        self.access_token = "test_token"
        self.client = WMCApiClient(self.base_url, self.access_token)

    def test_init_default_version(self):
        """初期化でデフォルトバージョンが設定されることをテスト"""
        client = WMCApiClient(self.base_url, self.access_token)
        assert client.base_url == self.base_url
        assert client.access_token == self.access_token
        assert client.api_version == "v1.2"

    def test_init_custom_version(self):
        """初期化でカスタムバージョンが設定されることをテスト"""
        client = WMCApiClient(self.base_url, self.access_token, api_version="v2.0")
        assert client.api_version == "v2.0"

    def test_init_base_url_strip(self):
        """ベースURLの末尾スラッシュが削除されることをテスト"""
        client = WMCApiClient("https://example.com/", self.access_token)
        assert client.base_url == "https://example.com"

    def test_get_headers(self):
        """ヘッダーが正しく生成されることをテスト"""
        headers = self.client._get_headers()
        expected = {
            "Authorization": self.access_token,
            "Content-Type": "application/json",
        }
        assert headers == expected

    def test_get_request(self, mocker):
        """GETリクエストが正しく実行されることをテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        result = self.client.get("/winactors", params={"limit": 10})

        # 検証
        mock_request.assert_called_once_with(
            method="GET",
            url="https://example.com/v1.2/winactors",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            json=None,
            params={"limit": 10},
            files=None,
            timeout=30,
        )
        assert result == {"data": "test"}

    def test_post_request_with_data(self, mocker):
        """POSTリクエスト（データ付き）が正しく実行されることをテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"id": 123}'
        mock_response.json.return_value = {"id": 123}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        data = {"name": "テストシナリオ"}
        result = self.client.post("/scenarios", data=data)

        # 検証
        mock_request.assert_called_once_with(
            method="POST",
            url="https://example.com/v1.2/scenarios",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            json=data,
            params=None,
            files=None,
            timeout=30,
        )
        assert result == {"id": 123}

    def test_post_request_with_files(self, mocker):
        """POSTリクエスト（ファイル付き）が正しく実行されることをテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"file_id": 456}'
        mock_response.json.return_value = {"file_id": 456}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        files = {"file": ("test.txt", b"test content")}
        result = self.client.post("/files", files=files)

        # 検証
        mock_request.assert_called_once_with(
            method="POST",
            url="https://example.com/v1.2/files",
            headers={"Authorization": self.access_token},  # Content-Typeが削除される
            json=None,  # filesがある場合はjsonはNone
            params=None,
            files=files,
            timeout=30,
        )
        assert result == {"file_id": 456}

    def test_put_request(self, mocker):
        """PUTリクエストが正しく実行されることをテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        data = {"name": "更新されたシナリオ"}
        result = self.client.put("/scenarios/123", data=data)

        # 検証
        mock_request.assert_called_once_with(
            method="PUT",
            url="https://example.com/v1.2/scenarios/123",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            json=data,
            params=None,
            files=None,
            timeout=30,
        )
        assert result == {"success": True}

    def test_delete_request(self, mocker):
        """DELETEリクエストが正しく実行されることをテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b""

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        result = self.client.delete("/scenarios/123")

        # 検証
        mock_request.assert_called_once_with(
            method="DELETE",
            url="https://example.com/v1.2/scenarios/123",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            json=None,
            params=None,
            files=None,
            timeout=30,
        )
        assert result == {}  # 空のレスポンスは空の辞書

    def test_patch_request(self, mocker):
        """PATCHリクエストが正しく実行されることをテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"updated": true}'
        mock_response.json.return_value = {"updated": True}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        data = {"status": "active"}
        result = self.client.patch("/scenarios/123", data=data)

        # 検証
        mock_request.assert_called_once_with(
            method="PATCH",
            url="https://example.com/v1.2/scenarios/123",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            json=data,
            params=None,
            files=None,
            timeout=30,
        )
        assert result == {"updated": True}

    def test_handle_http_error_with_message(self, mocker):
        """HTTPエラー（メッセージ付き）の処理をテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        # 実際のrequests.exceptions.HTTPErrorを使用
        http_error = requests.exceptions.HTTPError("HTTP Error")
        mock_response.raise_for_status.side_effect = http_error
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "不正なリクエストです"}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        # 検証
        assert "APIエラー (400): 不正なリクエストです" in str(exc_info.value)

    def test_handle_http_error_without_message(self, mocker):
        """HTTPエラー（メッセージなし）の処理をテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        # 実際のrequests.exceptions.HTTPErrorを使用
        http_error = requests.exceptions.HTTPError("HTTP Error")
        mock_response.raise_for_status.side_effect = http_error
        mock_response.status_code = 500
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        # 検証
        assert "APIエラー (500):" in str(exc_info.value)

    def test_handle_connection_error(self, mocker):
        """通信エラーの処理をテスト"""
        # モックレスポンスの設定
        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.side_effect = Exception("Connection failed")

        # テスト実行
        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        # 検証
        assert "GET リクエストエラー: Connection failed" in str(exc_info.value)

    def test_empty_response(self, mocker):
        """空のレスポンスの処理をテスト"""
        # モックレスポンスの設定
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b""

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        # テスト実行
        result = self.client.delete("/scenarios/123")

        # 検証
        assert result == {}

    def test_custom_api_version_url(self, mocker):
        """カスタムAPIバージョンでURLが正しく構築されることをテスト"""
        client = WMCApiClient(self.base_url, self.access_token, api_version="v2.0")

        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        client.get("/winactors")

        # URLにカスタムバージョンが含まれることを確認
        args, kwargs = mock_request.call_args
        assert kwargs["url"] == "https://example.com/v2.0/winactors"
