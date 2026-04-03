"""
tools/__main__.py

開発ツールのランチャー。

使い方:
 poetry run python -m tools
"""

import subprocess
import sys

TOOLS = [
    ("1", "mkdocs-serve", "マニュアルプレビュー（http://localhost:8000）"),
    ("2", "mkdocs-build", "マニュアルビルド（ZIP 配布ファイル生成）"),
    ("3", "copy-to-public", "PyArmor 暗号化 + Public フォルダ配置"),
    ("4", "copy-to-public-plain", "Public フォルダ配置（暗号化なし・開発用）"),
    ("5", "copy-to-public-quick", "ソースのみ配置（ベンダリングスキップ）"),
    ("6", "release --bump patch", "パッチリリース（バージョンバンプ + ZIP）"),
]

COMMANDS = {
    "mkdocs-serve": [sys.executable, "-m", "tools.generate_manual", "--clean"],
    "mkdocs-build": [
        sys.executable,
        "-m",
        "tools.generate_manual",
        "--clean",
        "--build",
    ],
    "copy-to-public": [sys.executable, "-m", "tools.package_copy_to_public"],
    "copy-to-public-plain": [
        sys.executable,
        "-m",
        "tools.package_copy_to_public",
        "--no-pyarmor",
    ],
    "copy-to-public-quick": [
        sys.executable,
        "-m",
        "tools.package_copy_to_public",
        "--no-pyarmor",
        "--skip-vendor",
    ],
    "release --bump patch": [
        sys.executable,
        "-m",
        "tools.release",
        "--bump",
        "patch",
    ],
}

POST_COMMANDS = {
    "mkdocs-serve": [sys.executable, "-m", "mkdocs", "serve"],
}


def main():
    print("")
    print("=== 開発ツール ===")
    print("")
    for key, name, desc in TOOLS:
        print(f" {key}) {desc}")
    print(" q) 終了")
    print("")

    choice = input("番号を選択: ").strip()

    if choice == "q":
        return

    selected = None
    for key, name, _desc in TOOLS:
        if choice == key:
            selected = name
            break

    if selected is None:
        print(f"[ERROR] 無効な選択: {choice}")
        sys.exit(1)

    try:
        cmd = COMMANDS[selected]
        print(f"\n実行: {' '.join(cmd)}\n")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(result.returncode)

        post_cmd = POST_COMMANDS.get(selected)
        if post_cmd:
            print(f"\n実行: {' '.join(post_cmd)}\n")
            result = subprocess.run(post_cmd)

        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n中断しました。")
        sys.exit(0)


if __name__ == "__main__":
    main()
