import sys

sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\runtime")
sys.path.append(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

from winactor_for_wmc.files import post_files

# 各種パラメータ
BASE_URL = !WMC URL!  # type: ignore
TOKEN = !アクセストークン!  # type: ignore
FILE_PATH = !ファイル名!  # type: ignore
DEPARTMENT1 = !所属(親)!  # type: ignore
DEPARTMENT2 = !所属(子)!  # type: ignore
DEPARTMENT3 = !所属(孫)!  # type: ignore
FILE_TAG = !ファイルタグ!  # type: ignore
DESCRIPTION = !説明!  # type: ignore

def main(**kwargs):
    return post_files.run(**kwargs)

if __name__ == "__main__":
    # パラメータ整形
    file_data = {}

    # 常に "false" をセット
    file_data["autoDeleteFlag"] = "false"

    if FILE_TAG:
        FILE_TAG = FILE_TAG.strip()
        if FILE_TAG:
            file_data["fileTag"] = FILE_TAG

    if DESCRIPTION:
        DESCRIPTION = DESCRIPTION.strip()
        if DESCRIPTION:
            file_data["description"] = DESCRIPTION

    file_id = main(
        base_url=BASE_URL,
        token=TOKEN,
        file_path=FILE_PATH,
        file_data=file_data,
        department_name1=DEPARTMENT1,
        department_name2=DEPARTMENT2,
        department_name3=DEPARTMENT3,
    )
    winactor.set_variable($ファイルID$, file_id)  # type: ignore
