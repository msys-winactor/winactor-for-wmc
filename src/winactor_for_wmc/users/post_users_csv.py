from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    csv_file_path = kwargs.get("csv_file_path")
    import_data = kwargs.get("import_data") or {}

    # APIクライアント初期化
    client = WMCApiClient(base_url, token)
    endpoint = "/users/csv"

    # CSVファイルアップロードAPI呼び出し
    with open(csv_file_path, "rb") as f:
        files = {"file": f}
        response = client.post(endpoint, data=import_data, files=files)

    return response
