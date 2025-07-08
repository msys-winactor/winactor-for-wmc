import json

import requests


class WMCApiClient:
    """WinActor Manager API 通信クライアント"""

    def __init__(self, base_url, access_token, api_version="v1.2"):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.api_version = api_version

    def _get_headers(self):
        return {
            "Authorization": self.access_token,
            "Content-Type": "application/json",
        }

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            if not response.content:
                return {}
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_response = response.json()
                error = error_response.get("error", "Unknown")
                detail = error_response.get("detail", "No detail provided")
                instance = error_response.get("instance", "Unknown path")
                error_parameter = error_response.get("errorParameter")
            except (json.JSONDecodeError, ValueError):
                error = "Unknown"
                detail = str(e)
                instance = "Unknown path"
                error_parameter = None

            message = (
                f"APIエラー ({response.status_code}):\n"
                f"  error    : {error}\n"
                f"  detail   : {detail}\n"
                f"  instance : {instance}"
            )
            if error_parameter:
                message += f"\n  parameter: {error_parameter}"
            raise RuntimeError(message)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"通信エラー: {e}")
        except json.JSONDecodeError:
            raise RuntimeError("レスポンスの解析に失敗しました")

    def _request(self, method, endpoint, data=None, params=None, files=None):
        url = f"{self.base_url}/{self.api_version}{endpoint}"
        headers = self._get_headers()

        if files:
            headers.pop("Content-Type", None)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if not files else None,
                params=params,
                files=files,
                timeout=30,
            )
            return self._handle_response(response)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"{method} リクエストエラー: {e}")

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, files=None):
        return self._request("POST", endpoint, data=data, files=files)

    def put(self, endpoint, data=None):
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint):
        return self._request("DELETE", endpoint)

    def patch(self, endpoint, data=None):
        return self._request("PATCH", endpoint, data=data)

    def get_csv(self, endpoint, params=None, save_path=None):
        return self._download_file(endpoint, params, save_path, file_type="CSV")

    def download_file(self, endpoint, params=None, save_path=None):
        return self._download_file(endpoint, params, save_path, file_type="ファイル")

    def _download_file(self, endpoint, params, save_path, file_type="ファイル"):
        url = f"{self.base_url}/{self.api_version}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            if not save_path:
                raise ValueError("保存先のファイルパスを指定してください")

            with open(save_path, "wb") as f:
                f.write(response.content)

            return save_path

        except requests.exceptions.HTTPError as e:
            try:
                error_response = response.json()
                error = error_response.get("error", "Unknown")
                detail = error_response.get("detail", "No detail provided")
                instance = error_response.get("instance", "Unknown path")
                error_parameter = error_response.get("errorParameter")
            except (json.JSONDecodeError, ValueError):
                error = "Unknown"
                detail = str(e)
                instance = "Unknown path"
                error_parameter = None

            message = (
                f"{file_type}ダウンロード APIエラー ({response.status_code}):\n"
                f"  error    : {error}\n"
                f"  detail   : {detail}\n"
                f"  instance : {instance}"
            )
            if error_parameter:
                message += f"\n  parameter: {error_parameter}"
            raise RuntimeError(message)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"通信エラー: {e}")
        except Exception as e:
            raise RuntimeError(f"{file_type}ダウンロードエラー: {e}")
