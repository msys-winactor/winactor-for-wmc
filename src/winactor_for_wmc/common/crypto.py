"""
暗号化/復号化ユーティリティモジュール

AES-256-CBC暗号化の復号化機能を提供します。
CryptoJS互換のフォーマットに対応しています。
"""

import base64
import hashlib

from Crypto.Cipher import AES


def decrypt_aes_cbc(encrypted_data_b64: str, password: str) -> str:
    """
    AES-256-CBC暗号化されたデータを復号化
    CryptoJS互換: SHA256ハッシュをキーとして使用

    Args:
        encrypted_data_b64: Base64エンコードされた暗号化データ
        password: 復号化パスワード

    Returns:
        復号化された平文

    Raises:
        ValueError: 復号化に失敗した場合
    """
    try:
        # Base64デコード
        encrypted_bytes = base64.b64decode(encrypted_data_b64)

        # IV（最初の16バイト）と暗号文を分離
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]

        # CryptoJS互換: SHA256ハッシュでキー生成
        key = hashlib.sha256(password.encode("utf-8")).digest()

        # AES-CBC復号化
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)

        # PKCS7パディング除去
        if len(decrypted) == 0:
            return ""

        padding_length = decrypted[-1]
        if padding_length > len(decrypted) or padding_length == 0:
            raise ValueError(f"無効なパディング長: {padding_length}")

        plaintext = decrypted[:-padding_length]

        # 複数のエンコーディングを試行
        for encoding in ["utf-8", "shift_jis", "cp932", "latin-1"]:
            try:
                return plaintext.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue

        # 全てのエンコーディングで失敗した場合
        raise ValueError(f"復号化されたデータのデコードに失敗しました")

    except Exception as e:
        raise ValueError(f"復号化エラー: {e}")
