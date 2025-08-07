from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    user_id = kwargs.get("user_id")

    endpoint = f"/users/{user_id}"

    client = WMCApiClient(base_url, token)
    response = client.get(endpoint)
    return response
