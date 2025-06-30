import sys
import os
import getpass

sys.path.append("C:\\msys-winactor")
sys.path.append("C:\\Users\\Public\\msys-winactor\\libs")

import export_csv

# 各種パラメータ（WinActorの変数展開を想定）
BASE_URL = !BASE_URL!  # type: ignore
TOKEN = !TOKEN!        # type: ignore
CSV_SAVE_PATH = !CSV_SAVE_PATH!  # type: ignore

# BASE_URLの末尾に「/」がなければ足す
if not BASE_URL.endswith("/"):
    BASE_URL += "/"
CSV_EXPORT_URL = BASE_URL + "departments/csv"

params = {}

try:
    # 保存先ディレクトリがなければ作成
    save_dir = os.path.dirname(CSV_SAVE_PATH)
    os.makedirs(save_dir, exist_ok=True)

    # CSVファイルをダウンロード＆保存
    export_csv.export_csv(
        CSV_EXPORT_URL, TOKEN, params, save_path=CSV_SAVE_PATH
    )

except Exception as e:
    raise winactor.WinActorError(1, f"所属情報エクスポートエラー\n{str(e)}")  # type: ignore