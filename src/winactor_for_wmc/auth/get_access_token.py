from typing import Any, Dict, Optional

from winactor_for_wmc.common.token_manager import TokenManager


def run(**kwargs: Any) -> Optional[Dict[str, Any]]:
    try:
        base_url = kwargs.get("base_url")
        user_id = kwargs.get("user_id")
        password = kwargs.get("password")

        if not base_url:
            raise ValueError("URLが指定されていません。")
        if not user_id:
            raise ValueError("ユーザーIDが指定されていません。")

        tm = TokenManager(base_url, user_id)
        token = tm.get_token(password)

        return {"status": "success", "token": token}

    except Exception as e:
        raise RuntimeError(f"トークンの取得に失敗しました: {e}") from e
