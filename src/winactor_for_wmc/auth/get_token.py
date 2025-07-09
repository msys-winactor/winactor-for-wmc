from winactor_for_wmc.common.client import WMCApiClient


def get_access_token(base_url, user_id, password):
    # WMC APIクライアントのインスタンスを作成
    client = WMCApiClient(base_url, "")
    token_data = {"name": user_id, "password": password}
    return client.post("/tokens", data=token_data)


def run(**kwargs):
    try:
        # 引数の取得
        base_url = kwargs.get("base_url")
        user_id = kwargs.get("user_id")
        password = kwargs.get("password")

        # 引数のチェック
        if not base_url:
            raise ValueError("ベースURLが指定されていません。")
        if not user_id:
            raise ValueError("ユーザーIDが指定されていません。")
        if not password:
            raise ValueError("パスワードが指定されていません。")

        # 本処理：WMC APIを使用してトークン取得
        token = get_access_token(base_url, user_id, password)

        return token

    except Exception as e:
        raise RuntimeError(f"トークンの取得に失敗しました: {e}") from e
