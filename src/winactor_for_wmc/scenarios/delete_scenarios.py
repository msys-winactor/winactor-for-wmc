from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    scenario_id = kwargs.get("scenario_id")

    endpoint = f"/scenarios/{scenario_id}"

    client = WMCApiClient(base_url, token)

    response = client.delete(endpoint)

    return
