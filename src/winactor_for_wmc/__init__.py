"""
WinActor for WMC パッケージ

このパッケージはWinActorとWMCの連携に必要な機能を提供します。
"""

import sys
from pathlib import Path

# Vendorされた依存パッケージを使用するための初期化
_vendor_path = str(Path(__file__).parent / "_vendor")
if _vendor_path not in sys.path:
    sys.path.insert(0, _vendor_path)

# パッケージインポート時にライセンスチェックを実行
_license_checked = False


def _check_license_once():
    """パッケージインポート時に一度だけライセンスチェックを実行"""
    global _license_checked
    if _license_checked:
        return

    try:
        from .common.license_db import check_license

        check_license("WinActor for Manager on Cloud")
        _license_checked = True
    except Exception as e:
        # ライセンスチェック失敗時はエラーを発生させる
        raise RuntimeError(f"ライセンス検証エラー: {e}") from e


# パッケージインポート時にチェック実行
_check_license_once()
