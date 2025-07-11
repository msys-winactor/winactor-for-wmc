from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_id = kwargs.get("file_id")
    save_path = kwargs.get("save_path")

    client = WMCApiClient(base_url, token)
    endpoint = f"/files/{file_id}/content"
    # download_fileはファイル保存も行う
    return client.download_file(endpoint, params=None, save_path=save_path)
