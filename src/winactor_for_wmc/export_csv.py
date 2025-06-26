import requests


class ExportEventsCsvError(Exception):
    """CSVエクスポート時の独自例外"""

    pass


def export_events_csv(csv_url, token, params, save_path):
    headers = {"Authorization": token}
    try:
        response = requests.get(csv_url, headers=headers, params=params)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return save_path
        else:
            try:
                error_json = response.json()
            except Exception:
                error_json = {}
            raise ExportEventsCsvError(
                f"module: export_events_csv\n"
                f"status_code: {response.status_code}\n"
                f"error: {error_json.get('error', '')}\n"
                f"detail: {error_json.get('detail', '')}"
            )
    except Exception as e:
        # requests自体のエラーなど
        raise ExportEventsCsvError(str(e))
