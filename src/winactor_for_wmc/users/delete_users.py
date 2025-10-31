from winactor_for_wmc.common import user_utils
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    user_name = kwargs.get("user_name")

    # user_nameからuser_idを取得
    user_id = user_utils.get_user_id_by_name(base_url, token, user_name)

    endpoint = f"/users/{user_id}"
    client = WMCApiClient(base_url, token)
    client.delete(endpoint)

    return
