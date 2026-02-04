import sys
import datetime

sys.path.append(r"C:\Users\Public\msys-dx-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.tasks import get_tasks_archive_files

def unix_to_datetime(unix_time):
    """
    UNIXタイムをyyyy/mm/dd hh:mm:ss形式に変換
 
    Args:
        unix_time (int or float): UNIXタイムスタンプ（秒またはミリ秒）
 
    Returns:
        str: yyyy/mm/dd hh:mm:ss形式の文字列
    """
    if unix_time is None or unix_time == "":
        return ""
    
    try:
        # 文字列の場合は数値に変換
        if isinstance(unix_time, str):
            unix_time = float(unix_time)
        
        # ミリ秒単位かどうかを判定（13桁以上の場合はミリ秒とみなす）
        if unix_time > 9999999999:  # 10桁を超える場合（2001年以降の日付でミリ秒単位）
            unix_time = unix_time / 1000
        
        dt = datetime.datetime.fromtimestamp(unix_time)
        return dt.strftime('%Y/%m/%d %H:%M:%S')
    
    except (ValueError, TypeError, OSError) as e:
        return ""

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

    # WinActor変数へセット
    winactor.set_variable($アーカイブファイル件数$, total)                 # type: ignore
    winactor.set_variable($アーカイブファイルID$, archive_file_id)         # type: ignore
    winactor.set_variable($アーカイブファイル名$, archive_file_name)         # type: ignore
    winactor.set_variable($アーカイブ作成日時$, unix_to_datetime(created_time))                # type: ignore
   