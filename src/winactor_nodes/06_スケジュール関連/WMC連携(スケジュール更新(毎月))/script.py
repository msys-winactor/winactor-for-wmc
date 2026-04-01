import sys

sys.path.append(r"C:\Users\public\msys-winactor-adapters\libs")

from winactor_for_wmc.schedules import put_schedules

# 各種パラメータ
BASE_URL = !*WMC URL!  # type: ignore
TOKEN = !*アクセストークン!  # type: ignore
SCHEDULE_ID = !*スケジュールID!  # type: ignore
NAME = !*スケジュール名!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
SCENARIO_ID = !*シナリオID!  # type: ignore
WINACTOR = !実行WinActor(ID)!  # type: ignore
DAYOFMONTH = !毎月何日(1～31)!  # type: ignore
TASKTIME = !実行時間(hh:mm:ss)!  # type: ignore
ARCHIVE = !アーカイブ|シナリオ実行後に作業ディレクトリのアーカイブを作成しない,シナリオ実行後に作業ディレクトリのアーカイブを作成する!  # type: ignore
LOG = !ログ|シナリオ実行時のログを作業ディレクトリに出力しない,シナリオ実行時のログを作業ディレクトリに出力する!  # type: ignore
ONERROR = !異常発生時|シナリオ実行時に異常が発生した場合、クリーンし、次のシナリオの実行の準備をする,シナリオ実行時に異常が発生した場合、そこで停止させる!  # type: ignore
SENDMAIL = !終了後のメール送信|異常終了時のみ送信する,送信しない,終了時に送信する,正常終了時のみ送信する!  # type: ignore
RETRYNUM = !リトライ回数!  # type: ignore
RETRYINTERVAL = !リトライ間隔(秒)!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
STATUS = !状態|有効,無効!  # type: ignore

def main(**kwargs):
    return put_schedules.run(**kwargs)

if __name__ == "__main__":
    # 必須パラメータチェック
    missing_params = []
    if not BASE_URL or not str(BASE_URL).strip():
        missing_params.append("WMC URL")
    if not TOKEN or not str(TOKEN).strip():
        missing_params.append("アクセストークン")
    if not SCHEDULE_ID or not str(SCHEDULE_ID).strip():
        missing_params.append("スケジュールID")
    if not NAME or not str(NAME).strip():
        missing_params.append("スケジュール名")
    if not SCENARIO_ID or not str(SCENARIO_ID).strip():
        missing_params.append("シナリオID")
    if missing_params:
        raise winactor.WinActorError(1, f"必須パラメータが入力されていません: {', '.join(missing_params)}")  # type: ignore

    # 変換ロジック
    winactor_list = [w.strip() for w in WINACTOR.split(",") if w.strip()] if WINACTOR else []
    # 単一IDに変換
    winactor_id = winactor_list[0] if winactor_list else None


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
    if winactor_id:
        schedule_dict["winactor"] = winactor_id  # ← 単一IDで渡す

    if DAYOFMONTH:
        try:
            schedule_dict["dayOfMonth"] = int(DAYOFMONTH.strip())
        except Exception:
            pass

    if TASKTIME:
        schedule_dict["taskTime"] = TASKTIME.strip()

    schedule_dict["archive"] = archive_bool
    schedule_dict["log"] = log_bool
    schedule_dict["onError"] = onerror_val
    schedule_dict["sendMail"] = sendmail_val

    # RETRYNUM が空/空白のみでなければ、int に変換してセット
    if RETRYNUM is not None and str(RETRYNUM).strip():
        schedule_dict["retryNum"] = int(str(RETRYNUM).strip())

    # RETRYINTERVAL が空/空白のみでなければ、int に変換してセット
    if RETRYINTERVAL is not None and str(RETRYINTERVAL).strip():
        schedule_dict["retryInterval"] = int(str(RETRYINTERVAL).strip())

    if DESCRIPTION:
        schedule_dict["description"] = DESCRIPTION.strip()
    schedule_dict["status"] = status_val
    schedule_dict["kind"] = "monthly"

    # mainの呼び出し
    result = main(
        schedules_url=BASE_URL,
        departments_url=BASE_URL,
        token=TOKEN,
        schedule_id=SCHEDULE_ID,
        schedule_data=schedule_dict,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )
