from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_id = kwargs.get("file_id")
    file_data = kwargs.get("file_data") or {}

    endpoint = f"/files/{file_id}"
    client = WMCApiClient(base_url, token)

    # ファイル更新API呼び出し
    response = client.put(endpoint, data=file_data)

    return response
