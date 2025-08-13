from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    save_path = kwargs.get("save_path")
    params = kwargs.get("params", {})

    endpoint = "/schedules/csv"

    client = WMCApiClient(base_url, token)

    response = client.get_csv(endpoint, params=params, save_path=save_path)

    return
