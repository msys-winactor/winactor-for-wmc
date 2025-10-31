from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_id = kwargs.get("file_id")

    endpoint = f"/files/{file_id}"

    client = WMCApiClient(base_url, token)

    response = client.delete(endpoint)

    return response
