import base64
import hashlib
import json
import os
from typing import Optional

import requests
from cryptography.fernet import Fernet


def encode_url(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")


def get_token_path(base_url: str, user_id: str) -> str:
    appdata = os.environ["APPDATA"]
    encoded_url = encode_url(base_url)
    return os.path.join(
        appdata,
        "msys-winactor",
        "winactor_for_wmc",
        "tokens",
        encoded_url,
        f"{user_id}.json",
    )


def get_cipher(keyword: str = "msys_wmc") -> Fernet:
    digest = hashlib.sha256(keyword.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


class TokenManager:
    def __init__(self, base_url: str, user_id: str):
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.token_path = get_token_path(base_url, user_id)
        self.token_data = None
        self.cipher = get_cipher()

    def load_token(self) -> Optional[str]:
        if not os.path.exists(self.token_path):
            return None

        try:
            with open(self.token_path, "r", encoding="utf-8") as f:
                self.token_data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"トークンファイルの読み込みに失敗しました: {e}")

        try:
            decrypted_token = self.cipher.decrypt(
                self.token_data["token"].encode()
            ).decode()
            return decrypted_token
        except Exception:
            # 復号に失敗した場合は古いファイルを削除
            try:
                os.remove(self.token_path)
            except Exception:
                pass
            self.token_data = None
            return None

    def save_token(self, token_data: dict, password: Optional[str] = None):
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            encrypted_token = self.cipher.encrypt(token_data["token"].encode()).decode()
            save_data = {"token": encrypted_token}
            if password:
                save_data["_password"] = self.cipher.encrypt(password.encode()).decode()
            with open(self.token_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            self.token_data = save_data
        except Exception:
            raise

    def login(self, password: str):
        url = f"{self.base_url}/v1.2/tokens"
        try:
            response = requests.post(
                url, json={"name": self.user_id, "password": password}
            )
            response.raise_for_status()
            token_data = response.json()
            self.save_token(token_data, password=password)
        except Exception as e:
            raise RuntimeError(f"ログインエラー: {e}")

    def ensure_token(self, password: Optional[str] = None):
        token = self.load_token()
        if token:
            return

        if password is None:
            if self.token_data and "_password" in self.token_data:
                try:
                    password = self.cipher.decrypt(
                        self.token_data["_password"].encode()
                    ).decode()
                except Exception as e:
                    raise RuntimeError(f"保存されたパスワードの復号に失敗しました: {e}")
            else:
                raise RuntimeError(
                    "トークンが存在せず、パスワードも指定されていません。"
                )

        self.login(password)

    def verify_token(self, token: str) -> bool:
        """トークンが有効かどうかを検証する"""
        try:
            url = f"{self.base_url}/v1.2/user"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def get_token(self, password: Optional[str] = None) -> str:
        try:
            # 既存のトークンを確認
            token = self.load_token()
            if token and self.verify_token(token):
                return token

            # 新しいトークンを取得
            self.ensure_token(password)
            token = self.load_token()

            if not token:
                raise RuntimeError("トークンの取得に失敗しました")

            return token

        except Exception as e:
            raise RuntimeError(f"トークンの取得に失敗しました: {e}")
