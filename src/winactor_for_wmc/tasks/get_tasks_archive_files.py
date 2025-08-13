from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    task_id = kwargs.get("task_id")

    endpoint = f"/tasks/{task_id}/archive-files"

    client = WMCApiClient(base_url, token)
    response = client.get(endpoint)
    return response
