import sys

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from winactor_for_wmc.tasks import get_tasks_archive_files

def main(**kwargs):
    # run関数の呼び出し
    return get_tasks_archive_files.run(**kwargs)

if __name__ == "__main__":
    BASE_URL = !WMC URL!  # type: ignore
    TOKEN = !アクセストークン!  # type: ignore
    TASK_ID = !タスクID!  # type: ignore

    # mainの呼び出し
    result = main(base_url=BASE_URL, token=TOKEN, task_id=TASK_ID)

    # 総件数を取得
    total = result.get("total", 0) if isinstance(result, dict) else 0

    # 結果から最初のアーカイブファイル情報を取得
    items = result.get("items", []) if isinstance(result, dict) else []
    if items:
        first_item = items[0]
        archive_file_id = first_item.get("archiveFileId", "")
        archive_file_name = first_item.get("archiveFileName", "")
        created_time = first_item.get("createdTime", "")
    else:
        archive_file_id = ""
        archive_file_name = ""
        created_time = ""

    # WinActor変数へセット（WinActor環境でのみ有効）
    winactor.set_variable($アーカイブファイル総件数$, total)                 # type: ignore
    winactor.set_variable($アーカイブファイルID$, archive_file_id)         # type: ignore
    winactor.set_variable($アーカイブファイル名$, archive_file_name)         # type: ignore
    winactor.set_variable($アーカイブ作成日時$, created_time)                # type: ignore
   