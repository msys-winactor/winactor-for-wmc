import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.schedules import post_schedules

# 各種パラメータ
BASE_URL = !WMC URL!  # type: ignore
TOKEN = !アクセストークン!  # type: ignore
NAME = !スケジュール名!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
SCENARIO_ID = !シナリオID!  # type: ignore
WINACTORS = !実行WinActor(ID)!  # type: ignore
ARCHIVE = !アーカイブ|シナリオ実行後に作業ディレクトリのアーカイブを作成しない,シナリオ実行後に作業ディレクトリのアーカイブを作成する!  # type: ignore
LOG = !ログ|シナリオ実行時のログを作業ディレクトリに出力しない,シナリオ実行時のログを作業ディレクトリに出力する!  # type: ignore
ONERROR = !異常発生時|シナリオ実行時に異常が発生した場合、クリーンし、次のシナリオの実行の準備をする,シナリオ実行時に異常が発生した場合、そこで停止させる!  # type: ignore
SENDMAIL = !終了後のメール送信|異常終了時のみ送信する,送信しない,終了時に送信する,正常終了時のみ送信する!  # type: ignore
RETRYNUM = !リトライ回数!  # type: ignore
RETRYINTERVAL = !リトライ間隔(秒)!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
STATUS = !状態|有効,無効!  # type: ignore

def main(**kwargs):
    return post_schedules.run(**kwargs)

if __name__ == "__main__":
    # 変換ロジック
    winactor_list = [w.strip() for w in WINACTORS.split(",") if w.strip()] if WINACTORS else []

    # ARCHIVE 再代入
    if ARCHIVE == "シナリオ実行後に作業ディレクトリのアーカイブを作成しない":
        ARCHIVE = "false"
    elif ARCHIVE == "シナリオ実行後に作業ディレクトリのアーカイブを作成する":
        ARCHIVE = "true"
    archive_bool = ARCHIVE.strip().lower() == "true"

    # LOG 再代入
    if LOG == "シナリオ実行時のログを作業ディレクトリに出力しない":
        LOG = "false"
    elif LOG == "シナリオ実行時のログを作業ディレクトリに出力する":
        LOG = "true"
    log_bool = LOG.strip().lower() == "true"

    # ONERROR 再代入
    if ONERROR == "シナリオ実行時に異常が発生した場合、クリーンし、次のシナリオの実行の準備をする":
        ONERROR = "clean"
    elif ONERROR == "シナリオ実行時に異常が発生した場合、そこで停止させる":
        ONERROR = "halt"
    onerror_val = ONERROR.strip()

    # SENDMAIL 再代入
    if SENDMAIL == "異常終了時のみ送信する":
        SENDMAIL = "onError"
    elif SENDMAIL == "送信しない":
        SENDMAIL = "neither"
    elif SENDMAIL == "終了時に送信する":
        SENDMAIL = "both"
    elif SENDMAIL == "正常終了時のみ送信する":
        SENDMAIL = "onNormal"
    sendmail_val = SENDMAIL.strip()

    # STATUS 再代入
    if STATUS == "有効":
        STATUS = "enable"
    elif STATUS == "無効":
        STATUS = "disable"
    status_val = STATUS.strip()

    # schedule_dictの作成
    schedule_dict = {}
    if NAME:
        schedule_dict["name"] = NAME.strip()
    if SCENARIO_ID:
        schedule_dict["scenarioId"] = SCENARIO_ID.strip()
    if winactor_list:
        schedule_dict["winactors"] = winactor_list
    schedule_dict["archive"] = archive_bool
    schedule_dict["log"] = log_bool
    schedule_dict["onError"] = onerror_val
    schedule_dict["sendMail"] = sendmail_val
    schedule_dict["retryNum"] = int(RETRYNUM) if RETRYNUM and str(RETRYNUM).strip() else 0
    schedule_dict["retryInterval"] = int(RETRYINTERVAL) if RETRYINTERVAL and str(RETRYINTERVAL).strip() else 0
    if DESCRIPTION:
        schedule_dict["description"] = DESCRIPTION.strip()
    schedule_dict["kind"] = "immediately"
    schedule_dict["status"] = status_val

    # mainの呼び出し
    result = main(
        schedules_url=BASE_URL,
        departments_url=BASE_URL,
        token=TOKEN,
        schedule_data=schedule_dict,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )

    if isinstance(result, list) and len(result) > 0:
        first_item = result[0]
    else:
        first_item = result
    schedule_id = first_item.get("id", "")
    # winactor_id = first_item.get("winactorId", "")

    # WinActor変数へセット
    winactor.set_variable($スケジュールID$, schedule_id)    # type: ignore
    # winactor.set_variable($WinActorID$, winactor_id)         # type: ignore
