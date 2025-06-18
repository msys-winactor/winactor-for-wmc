from typing import Any, Dict, Optional


def get_access_token(user_id, password):
    return "dummy_token_for_{}".format(user_id)


def run(**kwargs: Any) -> Optional[Dict[str, Any]]:
    try:
        user_id = kwargs.get("user_id")
        password = kwargs.get("password")

        # 引数のチェック
        if not user_id:
            raise ValueError("ユーザーIDが指定されていません。")
        if not password:
            raise ValueError("パスワードが指定されていません。")

        # 本処理
        token = get_access_token(user_id, password)

        return {"status": "success", "token": token}

    except Exception as e:
        return {"status": "error", "message": str(e)}
