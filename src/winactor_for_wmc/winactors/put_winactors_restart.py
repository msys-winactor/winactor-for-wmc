from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    winactor_id = kwargs.get("winactor_id")

    endpoint = f"/winactors/{winactor_id}/restart"

    client = WMCApiClient(base_url, token)

    client.put(endpoint)

    return
