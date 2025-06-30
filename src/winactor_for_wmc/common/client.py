import json

import requests


class WMCApiClient:
    """WinActor Manager API 通信クライアント"""

    def __init__(self, base_url, access_token, api_version="v1.2"):
        """
        WMCクライアントを初期化

        Args:
            base_url: WMCのベースURL (例: https://example.com)
            access_token: アクセストークン
            api_version: APIバージョン (デフォルト: v1.2)
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.api_version = api_version

    def _get_headers(self):
        """API呼び出し用のヘッダーを取得"""
        return {
            "Authorization": self.access_token,
            "Content-Type": "application/json",
        }

    def _handle_response(self, response):
        """レスポンスの共通処理"""
        try:
            response.raise_for_status()
            # レスポンスが空の場合は空の辞書を返す
            if not response.content:
                return {}
            # JSONレスポンスを返す
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_response = response.json()
                error_detail = error_response.get("message", str(e))
            except (json.JSONDecodeError, ValueError):
                error_detail = str(e)

            raise RuntimeError(f"APIエラー ({response.status_code}): {error_detail}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"通信エラー: {e}")
        except json.JSONDecodeError:
            raise RuntimeError("レスポンスの解析に失敗しました")

    def _request(self, method, endpoint, data=None, params=None, files=None):
        """共通のリクエスト処理"""
        url = f"{self.base_url}/{self.api_version}{endpoint}"
        headers = self._get_headers()

        # ファイルアップロードの場合はContent-Typeを削除
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
        """GET リクエストを実行"""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, files=None):
        """POST リクエストを実行"""
        return self._request("POST", endpoint, data=data, files=files)

    def put(self, endpoint, data=None):
        """PUT リクエストを実行"""
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint):
        """DELETE リクエストを実行"""
        return self._request("DELETE", endpoint)

    def patch(self, endpoint, data=None):
        """PATCH リクエストを実行"""
        return self._request("PATCH", endpoint, data=data)
