import sys
import os
import getpass

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

import post_files

# 各種パラメータ
BASE_URL = !BASE_URL!  # type: ignore
TOKEN = !TOKEN!  # type: ignore
FILE_PATH = !ファイル名!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
AUTO_DELETE_FLAG = !自動削除フラグ|false,true!  # type: ignore
FILE_TAG = !ファイルタグ!  # type: ignore

# BASE_URLの末尾に「/」がなければ足す
if not BASE_URL.endswith("/"):
    BASE_URL += "/"
FILES_URL = BASE_URL + "files"
DEPARTMENTS_URL = BASE_URL + "departments"

# パラメータ整形
file_data = {}

if AUTO_DELETE_FLAG:
    AUTO_DELETE_FLAG = AUTO_DELETE_FLAG.strip().lower()
    if AUTO_DELETE_FLAG == "true":
        file_data["autoDeleteFlag"] = "true"
    elif AUTO_DELETE_FLAG == "false":
        file_data["autoDeleteFlag"] = "false"

# ファイルタグ再代入
if FILE_TAG == "未設定":
    FILE_TAG = ""
elif FILE_TAG == "シナリオファイル(UMS)":
    FILE_TAG = "UMS"
elif FILE_TAG == "アーカイブファイル(ARC)":
    FILE_TAG = "ARC"
elif FILE_TAG == "データ一覧ファイル(DLF)":
    FILE_TAG = "DLF"
elif FILE_TAG == "出力ファイル(OPF)":
    FILE_TAG = "OPF"

if FILE_TAG:
    FILE_TAG = FILE_TAG.strip()
    if FILE_TAG:
        file_data["fileTag"] = FILE_TAG

try:
    file_id = post_files.upload_file_with_department_names(
        FILES_URL,
        DEPARTMENTS_URL,
        TOKEN,
        FILE_PATH,
        file_data,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )
    winactor.set_variable($ファイルID$, file_id)  # type: ignore

except Exception as e:
    raise winactor.WinActorError(1, f"ファイルアップロードエラー\n{str(e)}")  # type: ignore