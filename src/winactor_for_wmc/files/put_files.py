import os

from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    file_id = kwargs.get("file_id")
    file_path = kwargs.get("file_path")
    file_data = kwargs.get("file_data") or {}

    # 文字列化（フォームは基本テキスト）
    form_fields = {}
    for k, v in file_data.items():
        if v is None:
            continue
        s = str(v).strip()
        if s:
            form_fields[k] = s

    client = WMCApiClient(base_url, token)
    endpoint = f"/files/{file_id}"

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        files = {
            # (送信時のファイル名, ファイルobj, MIME)
            "file": (filename, f, "application/octet-stream"),
        }
        # ← data=form_fields, files=files を同時に渡す（multipart/form-data）
        response = client.put(endpoint, data=form_fields, files=files)
        return response
