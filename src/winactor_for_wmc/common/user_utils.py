from winactor_for_wmc.common.client import WMCApiClient


def get_user_id_by_name(base_url, token, user_name):
    """
    ユーザ名からユーザIDを取得する
    """
    client = WMCApiClient(base_url, token)
    endpoint = "/users"
    params = {"name": user_name, "nameType": "perfect", "size": 1}
    response = client.get(endpoint, params=params)
    return response["items"][0]["id"]
