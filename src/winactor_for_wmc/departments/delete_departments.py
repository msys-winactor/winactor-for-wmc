from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    department_id = kwargs.get("department_id")

    endpoint = f"/departments/{department_id}"

    client = WMCApiClient(base_url, token)

    client.delete(endpoint)

    return
