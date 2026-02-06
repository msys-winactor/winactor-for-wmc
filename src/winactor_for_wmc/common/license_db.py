"""
ライセンスデータベース管理モジュール

JSONファイルからライセンス情報を取得・検証する機能を提供します。
"""

import base64
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

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

# デフォルトのライセンスファイルパス（Windows）
DEFAULT_JSON_PATH = os.path.expandvars(
    r"%PUBLIC%\msys-winactor-adapters\licenses\licenses.json"
)


def sha256_hex(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def normalize_arch(arch: str) -> str:
    a = (arch or "").lower()
    if a == "amd64":
        return "x64"
    return a


def get_primary_mac() -> str:
    """
    最も一般的なMACアドレスを高速取得（uuid.getnode()使用）

    Returns:
        MACアドレス文字列（コロン区切り小文字）
    """
    return ":".join(
        f"{(uuid.getnode() >> shift) & 0xFF:02x}" for shift in range(40, -1, -8)
    )


def get_all_mac_addresses() -> list[str]:
    """
    すべての有効なMACアドレスを優先順位付きで取得（getmacコマンド使用）
    遅いので必要な時のみ呼び出すこと。
    優先順位: Wi-Fi > Ethernet > その他

    Returns:
        MACアドレスのリスト（優先順位順）
    """
    if sys.platform == "win32":
        try:
            # getmac コマンドでMACアドレス一覧を取得
            out = subprocess.check_output(
                ["getmac", "/fo", "csv", "/v"], text=True, encoding="cp437"
            )
            lines = [ln.strip() for ln in out.splitlines() if ln.strip()]

            # ヘッダー行をスキップ
            if lines:
                lines = lines[1:]

            wifi_macs = []
            ethernet_macs = []
            other_macs = []

            for line in lines:
                # CSV形式: "接続名","アダプター","物理アドレス","トランスポート名"
                parts = line.split('","')
                if len(parts) < 3:
                    continue

                conn_name = parts[0].strip('"').lower()
                mac = parts[2].strip('"').replace("-", ":").lower()

                # 無効なMACを除外
                if (
                    not mac
                    or len(mac) < 17
                    or mac == "n/a"
                    or mac.startswith("00:00:00")
                ):
                    continue

                # Bluetoothを除外
                if "bluetooth" in conn_name:
                    continue

                # 優先順位で分類
                if "wi-fi" in conn_name:
                    wifi_macs.append(mac)
                elif "ethernet" in conn_name or "イーサネット" in conn_name:
                    ethernet_macs.append(mac)
                else:
                    other_macs.append(mac)

            # 優先順位順に結合（重複除去）
            all_macs = wifi_macs + ethernet_macs + other_macs
            if all_macs:
                return list(dict.fromkeys(all_macs))

        except Exception:
            pass

    # フォールバック: uuid.getnode()
    return [get_primary_mac()]


def get_mac_colon_lower() -> str:
    """
    物理的なネットワークアダプターのMACアドレスを取得（後方互換性用）
    高速なuuid.getnode()を使用
    """
    return get_primary_mac()


def get_cpu_raw() -> str:
    """CPU情報を取得（Windowsではレジストリから取得）"""
    if sys.platform == "win32":
        try:
            import winreg

            # レジストリからCPU名を取得
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            )
            cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            winreg.CloseKey(key)
            if cpu_name:
                return cpu_name.strip()
        except Exception:
            pass
    return platform.processor() or ""


def get_hardware_hash(mac_address: str = None) -> dict:
    """
    現在のマシンのハードウェアハッシュを取得

    Args:
        mac_address: 使用するMACアドレス（Noneの場合は優先順位最高のMACを使用）

    Returns:
        {"mac": "...", "hostname": "...", "fingerprint": "..."}
    """
    import socket

    if mac_address is None:
        mac_address = get_mac_colon_lower()

    mac_raw = mac_address.strip().lower()
    hostname_raw = socket.gethostname().strip().lower()

    mac_h = sha256_hex(mac_raw)
    hostname_h = sha256_hex(hostname_raw)

    combined = f"{mac_raw}|{hostname_raw}"
    fingerprint = sha256_hex(combined)

    return {
        "mac": mac_h,
        "hostname": hostname_h,
        "fingerprint": fingerprint,
        "_debug_combined": combined,  # デバッグ用: ハッシュ前の文字列
    }


def verify_signed_license(signed_license: dict) -> dict:
    if signed_license.get("alg") != "rsa2048-sha256":
        raise ValueError(f"未対応のアルゴリズム: {signed_license.get('alg')}")

    payload_bytes = base64.b64decode(signed_license["payload"])
    sig_bytes = base64.b64decode(signed_license["sig"])

    public_key = RSA.import_key(RSA_PUBLIC_KEY)
    h = SHA256.new(payload_bytes)

    try:
        pkcs1_15.new(public_key).verify(h, sig_bytes)
    except (ValueError, TypeError) as e:
        raise ValueError(f"署名検証に失敗しました: {e}")

    return json.loads(payload_bytes.decode("utf-8"))


@dataclass
class LicenseRecord:
    id: int
    signed_license: str
    product_name: str
    created_at: str
    updated_at: str


@dataclass
class LicenseInfo:
    product_name: str
    license_type: str
    license_key: str
    expiry_date: Optional[str]
    auth_limit_date: Optional[str]
    raw_data: dict  # 復号化された完全なデータ


class LicenseDatabase:
    def __init__(self, json_path: str = DEFAULT_JSON_PATH):
        self.json_path = json_path

    def get_all_licenses(self) -> list["LicenseRecord"]:
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(
                f"ライセンスファイルが見つかりません: {self.json_path}"
            )

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise RuntimeError("ライセンスファイルの形式が不正です")

        return [
            LicenseRecord(
                id=item["id"],
                signed_license=item["signed_license"],
                product_name=item["product_name"],
                created_at=item["createdAt"],
                updated_at=item["updatedAt"],
            )
            for item in data
        ]

    def get_license_by_product(self, product_name: str) -> Optional["LicenseRecord"]:
        for lic in self.get_all_licenses():
            if lic.product_name == product_name:
                return lic
        return None

    def verify_license_data(self, signed_license_str: str) -> "LicenseInfo":
        signed_license = json.loads(signed_license_str)
        payload = verify_signed_license(signed_license)

        return LicenseInfo(
            product_name=payload.get("product_name", ""),
            license_type=payload.get("license_type", ""),
            license_key=payload.get("license_key", "N/A"),
            expiry_date=payload.get("expiry_date"),
            auth_limit_date=payload.get("auth_limit_date"),
            raw_data=payload,
        )

    def verify_license(self, product_name: str) -> tuple[bool, Optional[str]]:
        record = self.get_license_by_product(product_name)
        if record is None:
            return False, f"製品 '{product_name}' のライセンスが見つかりません"

        try:
            license_info = self.verify_license_data(record.signed_license)
        except ValueError as e:
            return False, f"ライセンスの検証に失敗しました: {e}"

        if license_info.license_type == "NL":
            return self._verify_named_license(license_info)
        return self._verify_standard_license(license_info)

    def _verify_named_license(
        self, license_info: "LicenseInfo"
    ) -> tuple[bool, Optional[str]]:
        license_hw = license_info.raw_data.get("hw_hash", {})

        if license_hw:
            license_fp = license_hw.get("fingerprint")

            # 高速化: まずprimary MACで検証
            primary_mac = get_primary_mac()
            current_hw = get_hardware_hash(primary_mac)
            current_fp = current_hw.get("fingerprint")

            if license_fp == current_fp:
                # Primary MACで一致（高速パス）
                return True, None

            # Primary MACで不一致の場合のみ、全MACアドレスで検証（遅いパス）
            all_macs = get_all_mac_addresses()
            matched = False
            last_tried_hw = current_hw

            for mac in all_macs:
                if mac == primary_mac:
                    continue  # すでに試したのでスキップ

                current_hw = get_hardware_hash(mac)
                current_fp = current_hw.get("fingerprint")

                if license_fp == current_fp:
                    matched = True
                    break

                last_tried_hw = current_hw  # デバッグ用に最後の試行を保存

            if not matched:
                # すべてのMACアドレスで不一致の場合のみエラー
                combined_str = (
                    last_tried_hw.get("_debug_combined", "N/A")
                    if last_tried_hw
                    else "N/A"
                )
                current_fp = (
                    last_tried_hw.get("fingerprint", "N/A") if last_tried_hw else "N/A"
                )

                msg = (
                    f"【ハードウェアハッシュ不一致】\n\n"
                    f"■ ハッシュ前の文字列（最後の試行）:\n{combined_str}\n\n"
                    f"■ ハッシュ後 (fingerprint):\n{current_fp}\n\n"
                    f"■ ライセンスファイルのfingerprint:\n{license_fp}\n\n"
                    f"■ 試行したMACアドレス数: {len(all_macs) + 1}"  # +1 for primary
                )
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0, msg, "ライセンス検証デバッグ", 0x40
                    )
                except:
                    pass

                return False, (
                    "ライセンスのハードウェア情報が一致しません。\n"
                    "このライセンスは別のマシン用です。"
                )

        if license_info.expiry_date:
            try:
                expiry = datetime.fromisoformat(
                    license_info.expiry_date.replace("Z", "+00:00")
                )
                now = datetime.now(expiry.tzinfo)
                if now > expiry:
                    last_date = expiry + timedelta(days=90)
                    last_date_str = last_date.strftime("%Y-%m-%d")
                    expiry_str = expiry.strftime("%Y-%m-%d")
                    message = (
                        f"WinActor for WMCのライセンス期限が切れております。\n"
                        f"ライセンス期限：～{expiry_str}\n"
                        f"恐れ入りますが丸紅情報システムズ営業担当までご連絡をお願いいたします。\n\n"
                        f"更新をご希望ではない場合、本ライブラリにつきましては\n"
                        f"{last_date_str}をもって利用が出来なくなります為ご注意ください。"
                    )
                    if now > last_date:
                        return (
                            False,
                            f"ライセンスの最終利用可能日を超過しています。\n{message}",
                        )
                    print(f"[警告] {message}")
            except ValueError:
                pass

        return True, None

    def _verify_standard_license(
        self, license_info: "LicenseInfo"
    ) -> tuple[bool, Optional[str]]:
        if license_info.expiry_date:
            try:
                expiry = datetime.fromisoformat(
                    license_info.expiry_date.replace("Z", "+00:00")
                )
                if datetime.now(expiry.tzinfo) > expiry:
                    return (
                        False,
                        f"ライセンスの有効期限が切れています: {license_info.expiry_date}",
                    )
            except ValueError:
                pass
        return True, None


def check_license(product_name: str, json_path: str = DEFAULT_JSON_PATH) -> bool:
    db = LicenseDatabase(json_path=json_path)
    valid, error = db.verify_license(product_name)
    if not valid:
        raise RuntimeError(f"ライセンスチェック失敗: {error}")
    return True
