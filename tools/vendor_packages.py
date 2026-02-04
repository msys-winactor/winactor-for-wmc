"""
依存パッケージをvendorフォルダにコピーするスクリプト
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def vendor_dependencies():
    """依存パッケージを_vendorフォルダにコピー"""
    # プロジェクトルートとvendorディレクトリ
    project_root = Path(__file__).parent.parent
    vendor_dir = project_root / "src" / "winactor_for_wmc" / "_vendor"

    # vendorディレクトリをクリーンアップ
    if vendor_dir.exists():
        shutil.rmtree(vendor_dir)
    vendor_dir.mkdir(parents=True, exist_ok=True)

    # __init__.pyを作成
    init_file = vendor_dir / "__init__.py"
    init_file.write_text('"""Vendored dependencies"""\n', encoding="utf-8")

    # 依存パッケージのリスト
    dependencies = [
        "requests",
        "Crypto",  # pycryptodomeのパッケージ名
        "certifi",
        "charset_normalizer",
        "idna",
        "urllib3",
    ]

    # 一時ディレクトリに依存関係をインストール
    temp_dir = project_root / ".temp_vendor"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)

    print("依存パッケージをダウンロード中...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(temp_dir),
            "requests>=2.32.3,<3.0.0",
            "pycryptodome>=3.21.0",
        ],
        check=True,
    )

    # 必要なパッケージをvendorディレクトリにコピー
    print("パッケージをvendorフォルダにコピー中...")
    for dep in dependencies:
        src_path = temp_dir / dep
        if src_path.exists():
            dst_path = vendor_dir / dep
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
                print(f"  コピー完了: {dep}")
            else:
                print(f"  スキップ（ディレクトリではない）: {dep}")
        else:
            print(f"  警告: {dep} が見つかりません")

    # .dist-infoや__pycache__などを削除
    print("不要なファイルをクリーンアップ中...")
    for item in vendor_dir.rglob("*"):
        if item.is_dir():
            if item.name in ["__pycache__", "tests", "test"]:
                shutil.rmtree(item)
            elif item.suffix == ".dist-info" or item.suffix == ".egg-info":
                shutil.rmtree(item)

    # 一時ディレクトリを削除
    shutil.rmtree(temp_dir)

    print(f"\n✓ vendoring完了: {vendor_dir}")


if __name__ == "__main__":
    vendor_dependencies()
