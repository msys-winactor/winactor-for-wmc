"""
WinActor for WMC パッケージ

このパッケージは WinActor と WMC の連携に必要な機能を提供します。
"""

import os
import sys
from pathlib import Path

# Vendor された依存パッケージを使用するための初期化
_vendor_path = str(Path(__file__).resolve().parent / "_vendor")
if _vendor_path not in sys.path:
    sys.path.insert(0, _vendor_path)

# cryptography の _rust 拡張は OpenSSL DLL (libcrypto-*.dll / libssl-*.dll) に依存する。
# delvewheel が cryptography.libs/ に配置した DLL をDLL検索パスに登録しておく。
if sys.platform == "win32":
    _crypto_libs = os.path.join(_vendor_path, "cryptography.libs")
    if os.path.isdir(_crypto_libs):
        os.add_dll_directory(_crypto_libs)

# パッケージインポート時にライセンスチェックを実行
_license_checked = False


def _check_license_once() -> None:
    """パッケージインポート時に一度だけライセンスチェックを実行"""
    global _license_checked
    if _license_checked:
        return

    try:
        from .common.license import check_license

        check_license("wmc")  # ← 製品タグ
        _license_checked = True
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"ライセンス検証エラー: {e}") from e


# パッケージインポート時にチェック実行
_check_license_once()
