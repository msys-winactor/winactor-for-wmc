# tests/test_client.py
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
        client = WMCApiClient(self.base_url, self.access_token)
        assert client.base_url == self.base_url
        assert client.access_token == self.access_token
        assert client.api_version == "v1.2"

    def test_init_custom_version(self):
        client = WMCApiClient(self.base_url, self.access_token, api_version="v2.0")
        assert client.api_version == "v2.0"

    def test_init_base_url_strip(self):
        client = WMCApiClient("https://example.com/", self.access_token)
        assert client.base_url == "https://example.com"

    def test_get_headers(self):
        headers = self.client._get_headers()
        expected = {
            "Authorization": self.access_token,
            "Content-Type": "application/json",
        }
        assert headers == expected

    def test_get_request(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        result = self.client.get("/winactors", params={"limit": 10})

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
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"id": 123}'
        mock_response.json.return_value = {"id": 123}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        data = {"name": "テストシナリオ"}
        result = self.client.post("/scenarios", data=data)

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
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"file_id": 456}'
        mock_response.json.return_value = {"file_id": 456}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        files = {"file": ("test.txt", b"test content")}
        result = self.client.post("/files", files=files)

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
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {"success": True}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        data = {"name": "更新されたシナリオ"}
        result = self.client.put("/scenarios/123", data=data)

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
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b""

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        result = self.client.delete("/scenarios/123")

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
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"updated": true}'
        mock_response.json.return_value = {"updated": True}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        data = {"status": "active"}
        result = self.client.patch("/scenarios/123", data=data)

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
        mock_response = mocker.Mock()
        http_error = requests.exceptions.HTTPError("HTTP Error")
        mock_response.raise_for_status.side_effect = http_error
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "INVALID_REQUEST",
            "detail": "不正なリクエストです",
            "instance": "/winactors",
        }

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        error_msg = str(exc_info.value)
        assert "APIエラー (400):" in error_msg
        assert "error    : INVALID_REQUEST" in error_msg
        assert "detail   : 不正なリクエストです" in error_msg
        assert "instance : /winactors" in error_msg

    def test_handle_http_error_with_error_parameter(self, mocker):
        """errorParameter が含まれるケースをテスト"""
        mock_response = mocker.Mock()
        http_error = requests.exceptions.HTTPError("Bad Request")
        mock_response.raise_for_status.side_effect = http_error
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "error": "INVALID_PARAMETER",
            "detail": "不正なパラメータです",
            "instance": "/winactors",
            "errorParameter": {"field": "name"},
        }

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        msg = str(exc_info.value)
        assert "APIエラー (422):" in msg
        assert "parameter: {'field': 'name'}" in msg

    def test_handle_http_error_without_message(self, mocker):
        mock_response = mocker.Mock()
        http_error = requests.exceptions.HTTPError("HTTP Error")
        mock_response.raise_for_status.side_effect = http_error
        mock_response.status_code = 500
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        assert "APIエラー (500):" in str(exc_info.value)

    def test_handle_invalid_json_on_success(self, mocker):
        """ステータスOKだが JSON 解析に失敗するケース"""
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"not-a-json"
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        assert "レスポンスの解析に失敗しました" in str(exc_info.value)

    def test_handle_request_exception_in_handle_response(self, mocker):
        """_handle_response 内で RequestException が発生した場合のラップメッセージをテスト"""
        client = WMCApiClient("https://example.com", "token")

        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.RequestException("network down")
        )

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            client.get("/winactors")

        assert "通信エラー: network down" in str(exc_info.value)

    def test_request_exception_wrapped(self, mocker):
        """requests.exceptions.RequestException もラップされること"""
        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.side_effect = requests.exceptions.RequestException("boom")

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get("/winactors")

        assert "GET リクエストエラー: boom" in str(exc_info.value)

    def test_request_wraps_non_runtimeerror_from_handle_response(self, mocker):
        """
        response.json() が ValueError を投げるなど、_handle_response が RuntimeError 以外を
        投げた場合でも _request が適切にラップすることを確認
        """
        client = WMCApiClient("https://example.com", "token")

        # 正常ステータスだが json() が ValueError を送出
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"has content"
        mock_response.json.side_effect = ValueError("not json value")

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            client.get("/winactors")

        # _request の except Exception によるラップメッセージ
        assert "GET リクエストエラー: not json value" in str(exc_info.value)

    def test_empty_response(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b""

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        result = self.client.delete("/scenarios/123")
        assert result == {}

    def test_custom_api_version_url(self, mocker):
        client = WMCApiClient(self.base_url, self.access_token, api_version="v2.0")

        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.request")
        mock_request.return_value = mock_response

        client.get("/winactors")

        args, kwargs = mock_request.call_args
        assert kwargs["url"] == "https://example.com/v2.0/winactors"

    def test_get_csv_success(self, mocker, tmp_path):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"id,name\n1,test"

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        csv_path = tmp_path / "test.csv"
        result = self.client.get_csv("/winactors/csv", save_path=str(csv_path))

        mock_request.assert_called_once_with(
            "https://example.com/v1.2/winactors/csv",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            params=None,
            timeout=30,
        )
        assert result == str(csv_path)
        assert csv_path.read_bytes() == b"id,name\n1,test"

    def test_get_csv_with_params(self, mocker, tmp_path):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"id,name,status\n1,test,active"

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        csv_path = tmp_path / "winactors.csv"

        params = {"encoding": "UTF-8", "sort": "name", "sort_direction": "ASC"}
        result = self.client.get_csv(
            "/winactors/csv", params=params, save_path=str(csv_path)
        )

        mock_request.assert_called_once_with(
            "https://example.com/v1.2/winactors/csv",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            params=params,
            timeout=30,
        )
        assert result == str(csv_path)

    def test_get_csv_no_save_path(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"id,name\n1,test"

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get_csv("/winactors/csv")

        assert "保存先のファイルパスを指定してください" in str(exc_info.value)

    def test_download_file_success(self, mocker, tmp_path):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"binary file content"

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        file_path = tmp_path / "downloaded_file.bin"
        result = self.client.download_file(
            "/files/123/content", save_path=str(file_path)
        )

        mock_request.assert_called_once_with(
            "https://example.com/v1.2/files/123/content",
            headers={
                "Authorization": self.access_token,
                "Content-Type": "application/json",
            },
            params=None,
            timeout=30,
        )
        assert result == str(file_path)
        assert file_path.read_bytes() == b"binary file content"

    def test_download_file_http_error(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Not Found"
        )
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": "FILE_NOT_FOUND",
            "detail": "ファイルが見つかりません",
            "instance": "/files/999/content",
        }

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.download_file("/files/999/content", save_path="/tmp/test.bin")

        error_msg = str(exc_info.value)
        assert "ファイルダウンロード APIエラー (404):" in error_msg
        assert "error    : FILE_NOT_FOUND" in error_msg
        assert "detail   : ファイルが見つかりません" in error_msg
        assert "instance : /files/999/content" in error_msg

    def test_download_file_http_error_with_error_parameter(self, mocker):
        """ダウンロードHTTPエラー時に errorParameter が含まれるケースをテスト"""
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Bad Request"
        )
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "INVALID_PARAMETER",
            "detail": "bad param",
            "instance": "/files/1/content",
            "errorParameter": {"field": "encoding"},
        }

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.download_file("/files/1/content", save_path="/tmp/a.bin")

        msg = str(exc_info.value)
        assert "ファイルダウンロード APIエラー (400):" in msg
        assert "parameter: {'field': 'encoding'}" in msg

    def test_download_file_http_error_non_json_body(self, mocker):
        """ダウンロード時のHTTPエラーでレスポンスがJSONでない場合"""
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Not Found"
        )
        mock_response.status_code = 404
        mock_response.json.side_effect = json.JSONDecodeError("bad", "", 0)

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.download_file("/files/999/content", save_path="/tmp/test.bin")

        msg = str(exc_info.value)
        assert "ファイルダウンロード APIエラー (404):" in msg
        # detail は例外文字列が入る
        assert "detail   : Not Found" in msg

    def test_csv_download_http_error(self, mocker):
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Forbidden"
        )
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": "PERMISSION_DENIED",
            "detail": "このリソースにアクセスする権限がありません",
            "instance": "/winactors/csv",
        }

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get_csv("/winactors/csv", save_path="/tmp/test.csv")

        error_msg = str(exc_info.value)
        assert "CSVダウンロード APIエラー (403):" in error_msg
        assert "error    : PERMISSION_DENIED" in error_msg

    def test_csv_download_http_error_with_error_parameter(self, mocker):
        """CSV ダウンロードHTTPエラーで errorParameter が含まれるケース"""
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Bad Request"
        )
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "INVALID_PARAMETER",
            "detail": "bad param",
            "instance": "/winactors/csv",
            "errorParameter": {"field": "encoding"},
        }

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.client.get_csv("/winactors/csv", save_path="/tmp/test.csv")

        msg = str(exc_info.value)
        assert "CSVダウンロード APIエラー (400):" in msg
        assert "parameter: {'field': 'encoding'}" in msg

    def test_download_file_request_exception(self, mocker):
        """requests.get が RequestException を送出する場合"""
        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.side_effect = requests.exceptions.RequestException("timeout")

        with pytest.raises(RuntimeError) as exc_info:
            self.client.download_file("/files/1/content", save_path="/tmp/a.bin")
        assert "通信エラー: timeout" in str(exc_info.value)

    def test_download_file_generic_exception_on_write(self, mocker):
        """ファイル書き込み時の例外ハンドリング（ファイルダウンロード）"""
        mock_response = mocker.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"data"

        mock_request = mocker.patch("winactor_for_wmc.common.client.requests.get")
        mock_request.return_value = mock_response

        # open を強制的に失敗させる
        mocker.patch("builtins.open", side_effect=Exception("disk full"))

        with pytest.raises(RuntimeError) as exc_info:
            self.client.download_file("/files/1/content", save_path="/tmp/a.bin")
        assert "ファイルダウンロードエラー: disk full" in str(exc_info.value)
