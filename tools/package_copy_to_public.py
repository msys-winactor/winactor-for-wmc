import shutil
from pathlib import Path

# プロジェクトルート基準の src ディレクトリ
SRC_DIR = Path(__file__).resolve().parent.parent / "src"

# コピー先ディレクトリ
DEST_DIR = Path(r"C:\Users\Public\msys-winactor\libs")

# 除外するディレクトリ名
EXCLUDE_DIRS = {"winactor_nodes"}


def main():
    # コピー先ディレクトリがなければ作成
    if not DEST_DIR.exists():
        print(f"📁 コピー先ディレクトリ {DEST_DIR} を作成します...")
        DEST_DIR.mkdir(parents=True, exist_ok=True)

    # src配下の __init__.py を含むパッケージで、除外対象でないものだけを選ぶ
    packages = [
        d
        for d in SRC_DIR.iterdir()
        if (d.is_dir() and (d / "__init__.py").exists() and d.name not in EXCLUDE_DIRS)
    ]

    if not packages:
        print("❌ 対象パッケージが見つかりません。")
        return

    for pkg in packages:
        dest_path = DEST_DIR / pkg.name

        # 既存のコピー先があれば削除
        if dest_path.exists():
            print(f"🧹 既存の {dest_path} を削除します...")
            shutil.rmtree(dest_path)

        print(f"📦 {pkg.name} を {dest_path} にコピーします...")
        shutil.copytree(pkg, dest_path)

    print("✅ コピー完了！")


if __name__ == "__main__":
    main()
