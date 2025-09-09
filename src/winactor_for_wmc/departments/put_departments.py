from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    department_id = kwargs.get("department_id")
    department_data = kwargs.get("department_data") or {}

    endpoint = f"/departments/{department_id}"
    client = WMCApiClient(base_url, token)

    # 所属更新API呼び出し (PUT /departments/{id})
    response = client.put(endpoint, data=department_data)

    return response
