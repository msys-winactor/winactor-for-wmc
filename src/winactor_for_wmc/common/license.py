"""
RSA2048-SHA256 署名検証によるライセンス認証モジュール。

依存: cryptography (_vendor/cryptography)
"""

import base64
import hashlib
import json
import os
import platform
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

# cryptography は _vendor/ 経由で利用（__init__.py で sys.path 挿入済み）
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ── 定数・パス ────────────────────────────────────────────────────────────────

DEFAULT_LICENSE_DIR = os.path.expandvars(r"%PUBLIC%\msys-winactor-adapters\licenses")

# RSA2048 公開鍵（PEM形式）
# 鍵の生成例: openssl genrsa -out private.pem 2048 && openssl rsa -in private.pem -pubout -out public.pem

# RSA公開鍵（ライセンス署名検証用）
RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3CCjuRxhBbxoznb2DI+N
vsCKlU2XmHFBdNzI966VV+8rIxQ+rVY+Mrt0u1kRNlek2A0hDz22SAcT4Z7zNOxq
5+TAKwikpto/NyTsyHwCuSDU0mIWBwlGnEC4+DRSO1EUkPogR9RiU5dmydQGdwcf
DfQSZzAlEkltv5nBUnTIwU7ON5tL6GEUb4gLDKF63pv9M1Hx9LSpvomz/nmEsxEC
z2jJQhpGNnvXjMhCYZ6WIA+v8ianBc23uqvRYD8DVqBl6oc8zVbGBOI+Js6BlAea
flm+PCNA2mYqtGoU5R08jVOlhPZ/xT/3wTJwMSmEsMQBhFgGzOJrIDr56sNTiQna
+QIDAQAB
-----END PUBLIC KEY-----"""

# NL: 有効期限切れ後の猶予日数
_NL_GRACE_DAYS = 90


def get_license_path(product_tag: str, license_dir: str = DEFAULT_LICENSE_DIR) -> str:
    """ライセンスファイルのフルパスを返す。"""
    return os.path.join(license_dir, f"{product_tag}_license.json")


# ── ハードウェアフィンガープリント（NL用） ────────────────────────────────────



def get_hardware_hash() -> dict:
    """
    ハードウェアフィンガープリントを計算して返す。

    fingerprint = SHA256(hostname_lower)

    Returns:
        {
            "hostname": hostname_lower,
            "fingerprint": SHA256(hostname_lower),
        }
    """
    hostname_lower = platform.node().lower()

    def _sha256(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    return {
        "hostname": hostname_lower,
        "fingerprint": _sha256(hostname_lower),
    }


# ── 署名検証 ──────────────────────────────────────────────────────────────────


def verify_signed_license(signed_license: dict) -> dict:
    """
    RSA2048-SHA256 署名を検証し、payload dict を返す。

    Args:
        signed_license: {"alg", "kid", "payload", "sig"} を含む dict

    Returns:
        デコード済み payload dict

    Raises:
        ValueError: 署名不正またはフォーマット不正
    """
    alg = signed_license.get("alg", "")
    payload_b64 = signed_license.get("payload", "")
    sig_b64 = signed_license.get("sig", "")

    if alg != "rsa2048-sha256" or not payload_b64 or not sig_b64:
        raise ValueError(
            "ライセンスファイルの形式が正しくありません。正規のライセンスファイルを使用してください。"
        )

    try:
        payload_bytes = base64.b64decode(payload_b64)
        sig_bytes = base64.b64decode(sig_b64)
    except Exception as e:
        raise ValueError(
            "ライセンスファイルの形式が正しくありません。正規のライセンスファイルを使用してください。"
        ) from e

    if "REPLACE_WITH_ACTUAL_PUBLIC_KEY" in RSA_PUBLIC_KEY:
        raise ValueError(
            "RSA公開鍵が設定されていません（license.py の RSA_PUBLIC_KEY を設定してください）"
        )

    try:
        public_key = serialization.load_pem_public_key(RSA_PUBLIC_KEY.encode("ascii"))
    except Exception as e:
        raise ValueError("RSA公開鍵の形式が正しくありません") from e

    try:
        public_key.verify(sig_bytes, payload_bytes, padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature as e:
        raise ValueError(
            "ライセンスファイルが正しくありません。正規のライセンスファイルを使用してください。"
        ) from e

    try:
        return json.loads(payload_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(
            "ライセンスファイルの形式が正しくありません。正規のライセンスファイルを使用してください。"
        ) from e


# ── データクラス ──────────────────────────────────────────────────────────────


@dataclass
class LicenseInfo:
    license_uid: str
    product_id: int
    product_name: str
    product_tag: str
    license_type: str
    expiry_date: Optional[str]
    auth_limit_date: Optional[str]
    is_migs: bool
    raw_data: dict


# ── LicenseFile クラス ────────────────────────────────────────────────────────


class LicenseFile:
    def __init__(
        self,
        product_tag: str,
        license_dir: str = DEFAULT_LICENSE_DIR,
    ) -> None:
        self.product_tag = product_tag
        self.license_dir = license_dir
        self._license_info: Optional[LicenseInfo] = None

    # ── 内部ユーティリティ ────────────────────────────────────────────────

    @staticmethod
    def _parse_expiry_date(expiry_str: str) -> date:
        """
        YYYY-MM-DD または ISO datetime 文字列を date に変換する。
        後方互換として ISO datetime も受け入れる。
        """
        if not expiry_str:
            raise ValueError("expiry_date が空です")
        # ISO datetime（T を含む場合）
        if "T" in expiry_str:
            return datetime.fromisoformat(expiry_str).date()
        return date.fromisoformat(expiry_str)

    def _verify_named_license(
        self, license_info: LicenseInfo
    ) -> tuple[bool, Optional[str]]:
        """NL（Named License）の検証。"""
        hw_hash = license_info.raw_data.get("hw_hash", {})
        expected_fingerprint = hw_hash.get("fingerprint")
        if not expected_fingerprint:
            return (
                False,
                "ライセンスファイルが正しくありません。正規のライセンスファイルを使用してください。",
            )

        # ── フィンガープリント照合（ホスト名ベース） ─────────────────
        current_hw = get_hardware_hash()
        if current_hw["fingerprint"] != expected_fingerprint:
            return (
                False,
                "このPCはライセンス登録されていません。ライセンスの再発行が必要です。",
            )

        # ── 有効期限チェック（NL: 90日猶予あり） ─────────────────────
        if license_info.expiry_date:
            try:
                expiry = self._parse_expiry_date(license_info.expiry_date)
            except ValueError as e:
                return False, f"expiry_date のパースに失敗しました: {e}"

            today = date.today()
            if today > expiry:
                grace_end = expiry + timedelta(days=_NL_GRACE_DAYS)
                if today <= grace_end:
                    remaining = (grace_end - today).days
                    print(
                        f"警告: ライセンスの有効期限が切れています（期限: {expiry}）。"
                        f"あと {remaining} 日以内に更新手続きを行ってください。",
                        file=sys.stderr,
                    )
                    # 猶予期間中は継続（True を返す）
                    return True, None
                else:
                    return (
                        False,
                        f"ライセンスの有効期限が切れています（期限: {expiry}）。更新手続きを行ってください。",
                    )

        return True, None

    def _verify_standard_license(
        self, license_info: LicenseInfo
    ) -> tuple[bool, Optional[str]]:
        """FL（Floating License）等の標準検証。"""
        if license_info.expiry_date:
            try:
                expiry = self._parse_expiry_date(license_info.expiry_date)
            except ValueError as e:
                return False, f"expiry_date のパースに失敗しました: {e}"

            today = date.today()
            if today > expiry:
                return (
                    False,
                    f"ライセンスの有効期限が切れています（期限: {expiry}）。更新手続きを行ってください。",
                )

        return True, None

    # ── 公開メソッド ──────────────────────────────────────────────────────

    def load(self) -> LicenseInfo:
        """ライセンスファイルを読み込み、署名検証を行い LicenseInfo を返す。"""
        license_path = get_license_path(self.product_tag, self.license_dir)

        if not os.path.exists(license_path):
            raise FileNotFoundError(
                f"認証が完了していません。ライセンスファイルを所定の場所に配置してください。\n"
                f"  場所: {license_path}"
            )

        with open(license_path, encoding="utf-8") as f:
            try:
                signed_license = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "ライセンスファイルの形式が正しくありません。正規のライセンスファイルを使用してください。"
                ) from e

        payload = verify_signed_license(signed_license)

        custom = payload.get("custom", {})
        self._license_info = LicenseInfo(
            license_uid=payload.get("license_uid", ""),
            product_id=int(payload.get("product_id", 0)),
            product_name=payload.get("product_name", ""),
            product_tag=payload.get("product_tag", ""),
            license_type=payload.get("license_type", ""),
            expiry_date=payload.get("expiry_date"),
            auth_limit_date=payload.get("auth_limit_date"),
            is_migs=str(custom.get("is_migs", "")).lower() == "true",
            raw_data=payload,
        )
        return self._license_info

    def verify(self) -> tuple[bool, Optional[str]]:
        """
        ライセンスの有効性をチェックする。load() が未実行の場合は内部で呼び出す。

        Returns:
            (True, None) または (False, エラーメッセージ)
        """
        if self._license_info is None:
            self.load()

        info = self._license_info
        assert info is not None  # load() が成功していれば None にならない

        # product_tag の一致確認
        if info.product_tag and info.product_tag != self.product_tag:
            return False, (
                f"ライセンスの product_tag が一致しません"
                f"（期待: {self.product_tag!r}, 実際: {info.product_tag!r}）"
            )

        if info.license_type == "NL":
            return self._verify_named_license(info)
        else:
            return self._verify_standard_license(info)


# ── 公開関数 ──────────────────────────────────────────────────────────────────


def get_license_info(
    product_tag: str,
    license_dir: str = DEFAULT_LICENSE_DIR,
) -> LicenseInfo:
    """
    ライセンスファイルを読み込み LicenseInfo を返す（署名検証のみ、有効性チェックなし）。

    Raises:
        RuntimeError: ファイルが見つからない・署名不正など
    """
    try:
        lf = LicenseFile(product_tag, license_dir)
        return lf.load()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(str(e)) from e


# ── ライセンス検証キャッシュ ──────────────────────────────────────────────────

_CACHE_TTL_SECONDS = 86400  # 24時間


def _get_cache_dir() -> str:
    """キャッシュファイルの格納ディレクトリを返す。"""
    local = os.environ.get("LOCALAPPDATA", "")
    if not local:
        local = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(local, "msys_winactor_adapters", "winactor_for_wmc")


def _get_license_cache_path(product_tag: str) -> str:
    """ライセンス検証キャッシュファイルのパスを返す。"""
    return os.path.join(_get_cache_dir(), f"{product_tag}_license_cache.json")


def _is_cache_valid(
    product_tag: str,
    license_dir: str = DEFAULT_LICENSE_DIR,
) -> bool:
    """
    キャッシュが有効かどうかを判定する。

    以下の条件をすべて満たす場合に True:
    - キャッシュファイルが存在する
    - ライセンスファイルの mtime がキャッシュ時と一致する
    - キャッシュ作成から TTL 以内である
    """
    cache_path = _get_license_cache_path(product_tag)
    if not os.path.exists(cache_path):
        return False

    try:
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        return False

    # ライセンスファイルの現在の mtime を取得
    license_path = get_license_path(product_tag, license_dir)
    if not os.path.exists(license_path):
        return False

    current_mtime = os.path.getmtime(license_path)
    cached_mtime = cache.get("license_mtime")
    if cached_mtime is None or current_mtime != cached_mtime:
        return False

    # TTL チェック
    cached_at = cache.get("cached_at", 0)
    import time

    if time.time() - cached_at > _CACHE_TTL_SECONDS:
        return False

    return True


def _save_cache(
    product_tag: str,
    license_dir: str = DEFAULT_LICENSE_DIR,
) -> None:
    """検証成功時にキャッシュを保存する。"""
    import time

    license_path = get_license_path(product_tag, license_dir)
    cache_data = {
        "license_mtime": os.path.getmtime(license_path),
        "cached_at": time.time(),
    }

    cache_path = _get_license_cache_path(product_tag)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)


# ── check_license ────────────────────────────────────────────────────────────


def check_license(
    product_tag: str,
    license_dir: str = DEFAULT_LICENSE_DIR,
) -> bool:
    """
    ライセンスをロードして検証する。

    前回の検証結果をキャッシュし、ライセンスファイルが変更されていなければ
    RSA 署名検証をスキップして高速に返す（TTL: 24時間）。

    Returns:
        True（有効）

    Raises:
        RuntimeError: ライセンスが無効または検証に失敗した場合
    """
    if _is_cache_valid(product_tag, license_dir):
        return True

    try:
        lf = LicenseFile(product_tag, license_dir)
        lf.load()
        valid, reason = lf.verify()
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(str(e)) from e

    if not valid:
        raise RuntimeError(reason)

    try:
        _save_cache(product_tag, license_dir)
    except Exception:
        pass  # キャッシュ保存失敗は無視（次回また検証するだけ）
    return True
