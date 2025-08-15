from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    schedule_id = kwargs.get("schedule_id")

    endpoint = f"/schedules/{schedule_id}/enable"

    client = WMCApiClient(base_url, token)

    response = client.put(endpoint)

    return
