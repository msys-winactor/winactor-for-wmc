import sys
import os
import json
import getpass

# モジュール検索パスを追加
sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

from auth import post_schedules

# 各種パラメータ
BASE_URL = !BASE_URL!  # type: ignore
TOKEN = !TOKEN!  # type: ignore
NAME = !スケジュール名!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
SCENARIO_ID = !シナリオID!  # type: ignore
WINACTORS = !実行WinActor(ID)!  # type: ignore
TASKDATE = !日付指定日(yyyy/MM/dd)!  # type: ignore
TASKTIME = !実行時間(hh:mm:ss)!  # type: ignore
ARCHIVE = !アーカイブ|シナリオ実行後に作業ディレクトリのアーカイブを作成しない,シナリオ実行後に作業ディレクトリのアーカイブを作成する!  # type: ignore
LOG = !ログ|シナリオ実行時のログを作業ディレクトリに出力しない,シナリオ実行時のログを作業ディレクトリに出力する!  # type: ignore
ONERROR = !異常発生時|シナリオ実行時に異常が発生した場合、クリーンし、次のシナリオの実行の準備をする,シナリオ実行時に異常が発生した場合、そこで停止させる!  # type: ignore
SENDMAIL = !終了後のメール送信|異常終了時のみ送信する,送信しない,終了時に送信する,正常終了時のみ送信する!  # type: ignore
RETRYNUM = !リトライ回数!  # type: ignore
RETRYINTERVAL = !リトライ間隔(秒)!  # type: ignore
DESCRIPTION = !メモ!  # type: ignore
STATUS = !状態|有効,無効!  # type: ignore


# KINDは固定
KIND = "specified"

# BASE_URLの末尾に「/」がなければ足す
if not BASE_URL.endswith("/"):
    BASE_URL += "/"
SCHEDULES_URL = BASE_URL + "schedules"
DEPARTMENTS_URL = BASE_URL + "departments"

schedule_dict = {}

# パラメータの型を設定

if NAME:
    NAME = NAME.strip()
    if NAME:
        schedule_dict["name"] = NAME

if DEPARTMENT1:
    try:
        schedule_dict["department1"] = int(DEPARTMENT1)
    except Exception:
        pass
if DEPARTMENT2:
    try:
        schedule_dict["department2"] = int(DEPARTMENT2)
    except Exception:
        pass
if DEPARTMENT3:
    try:
        schedule_dict["department3"] = int(DEPARTMENT3)
    except Exception:
        pass

if SCENARIO_ID:
    SCENARIO_ID = SCENARIO_ID.strip()
    if SCENARIO_ID:
        schedule_dict["scenarioId"] = SCENARIO_ID

if WINACTORS:
    WINACTORS = WINACTORS.strip()
    if WINACTORS:
        winactor_list = [w.strip() for w in WINACTORS.split(",") if w.strip()]
        if winactor_list:
            schedule_dict["winactors"] = winactor_list

if TASKDATE:
    TASKDATE = TASKDATE.strip()
    if TASKDATE:
        schedule_dict["taskDate"] = TASKDATE

if TASKTIME:
    TASKTIME = TASKTIME.strip()
    if TASKTIME:
        schedule_dict["taskTime"] = TASKTIME

#  再代入
if ARCHIVE == "シナリオ実行後に作業ディレクトリのアーカイブを作成しない":
    ARCHIVE = "false"
elif ARCHIVE == "シナリオ実行後に作業ディレクトリのアーカイブを作成する":
    ARCHIVE = "true"

if ARCHIVE:
    ARCHIVE = ARCHIVE.strip().lower()
    if ARCHIVE == "true":
        schedule_dict["archive"] = True
    elif ARCHIVE == "false":
        schedule_dict["archive"] = False

#  再代入
if LOG == "シナリオ実行時のログを作業ディレクトリに出力しない":
    LOG = "false"
elif LOG == "シナリオ実行時のログを作業ディレクトリに出力する":
    LOG = "true"

if LOG:
    LOG = LOG.strip().lower()
    if LOG == "true":
        schedule_dict["log"] = True
    elif LOG == "false":
        schedule_dict["log"] = False

# 再代入
if ONERROR == "シナリオ実行時に異常が発生した場合、クリーンし、次のシナリオの実行の準備をする":
    ONERROR = "clean"
elif ONERROR == "シナリオ実行時に異常が発生した場合、そこで停止させる":
    ONERROR = "halt"

if ONERROR:
    ONERROR = ONERROR.strip()
    if ONERROR:
        schedule_dict["onError"] = ONERROR

#  再代入
if SENDMAIL == "異常終了時のみ送信する":
    SENDMAIL = "onError"
elif SENDMAIL == "送信しない":
    SENDMAIL = "neither"
elif SENDMAIL == "終了時に送信する":
    SENDMAIL = "both"
elif SENDMAIL == "正常終了時のみ送信する":
    SENDMAIL = "onNormal"

if SENDMAIL:
    SENDMAIL = SENDMAIL.strip()
    if SENDMAIL:
        schedule_dict["sendMail"] = SENDMAIL
schedule_dict["kind"] = KIND

if RETRYNUM:
    RETRYNUM = RETRYNUM.strip()
    try:
        schedule_dict["retryNum"] = int(RETRYNUM)
    except Exception:
        pass

if RETRYINTERVAL:
    RETRYINTERVAL = RETRYINTERVAL.strip()
    try:
        schedule_dict["retryInterval"] = int(RETRYINTERVAL)
    except Exception:
        pass

if DESCRIPTION:
    DESCRIPTION = DESCRIPTION.strip()
    if DESCRIPTION:
        schedule_dict["description"] = DESCRIPTION

# 再代入
if STATUS == "有効":
    STATUS = "enable"
elif STATUS == "無効":
    STATUS = "disable"

if STATUS:
    STATUS = STATUS.strip()
    if STATUS:
        schedule_dict["status"] = STATUS


# 部門名からIDを取得し、スケジュール登録
try:

    result = post_schedules.register_schedule_with_department_names(
        SCHEDULES_URL,
        DEPARTMENTS_URL,
        TOKEN,
        schedule_dict,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3
    )
    # 返り値がリストなら最初の要素を使う
    if isinstance(result, list) and len(result) > 0:
        first_item = result[0]
    else:
        first_item = result
    schedule_id = first_item.get("id", "")
    winactor_id = first_item.get("winactorId", "")
    winactor.set_variable($スケジュールID$, schedule_id)    # type: ignore
    winactor.set_variable($WinActorID$, winactor_id)    # type: ignore

except Exception as e:
    raise winactor.WinActorError(1, f"スケジュール登録(日時指定)エラー\n{str(e)}")  # type: ignore