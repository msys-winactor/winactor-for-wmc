import requests


class DownloadFileError(Exception):
    """ファイルダウンロード時の独自例外"""

    pass


def download_file_content(files_content_url, token, file_id, save_path):
    """
    指定されたファイルIDのコンテンツをダウンロードし、ローカルに保存する
    """
    url = f"{files_content_url}/{file_id}/content"
    headers = {"Authorization": token}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return save_path
        else:
            try:
                error_json = response.json()
            except Exception:
                error_json = {}
            raise DownloadFileError(
                f"module: get_files_content\n"
                f"status_code: {response.status_code}\n"
                f"error: {error_json.get('error', '')}\n"
                f"detail: {error_json.get('detail', '')}"
            )
    except Exception as e:
        raise DownloadFileError(str(e))
