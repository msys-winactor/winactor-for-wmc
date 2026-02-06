import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# 標準出力のエンコーディングをUTF-8に設定
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# プロジェクトルート基準の src ディレクトリ
SRC_DIR = Path(__file__).resolve().parent.parent / "src"

# コピー先ディレクトリ
DEST_DIR = Path(r"C:\Users\Public\msys-winactor-adapters\libs\winactor_for_wmc")

# 除外するディレクトリ名
EXCLUDE_DIRS = {"winactor_nodes"}

# PyArmorコマンド解決用（遅延初期化）
PYARMOR_BIN = None
PYARMOR_CMD_DISPLAY = ""


def _python_available(py_tag: str) -> bool:
    """py -<version> コマンドが存在するかを確認"""
    try:
        subprocess.run(
            ["py", py_tag, "-c", "import sys"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _pyarmor_available(cmd: list[str]) -> bool:
    """指定コマンドでPyArmorが利用可能か確認"""
    try:
        subprocess.run(
            cmd + ["--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _resolve_pyarmor_command() -> list[str]:
    """WinActor互換のPyArmorコマンドを取得"""
    env_cmd = os.environ.get("PYARMOR_CMD")
    if env_cmd:
        return shlex.split(env_cmd, posix=False), env_cmd

    preferred_tag = os.environ.get("PYARMOR_PY_TAG", "-3.12-32")

    if not _python_available(preferred_tag):
        raise RuntimeError(
            "WinActorと同じ32bit Python (py {0}) が見つかりません。"
            " https://www.python.org/downloads/windows/ から 32bit Python をインストールするか、"
            "環境変数 PYARMOR_CMD で PyArmor 実行コマンドを指定してください。".format(
                preferred_tag
            )
        )

    # PyArmor 9.x exposes its CLI via pyarmor.cli.__main__ instead of pyarmor.__main__
    cmd = ["py", preferred_tag, "-m", "pyarmor.cli.__main__"]
    if not _pyarmor_available(cmd):
        raise RuntimeError(
            "Python {0} に PyArmor 9.2.3 がインストールされていません。"
            " 次を実行してください: py {0} -m pip install --upgrade pyarmor==9.2.3".format(
                preferred_tag
            )
        )

    return cmd, " ".join(cmd)


def get_pyarmor_command() -> list[str]:
    """PyArmorコマンドをキャッシュして返す"""
    global PYARMOR_BIN, PYARMOR_CMD_DISPLAY

    if PYARMOR_BIN is None:
        cmd, display = _resolve_pyarmor_command()
        PYARMOR_BIN = cmd
        PYARMOR_CMD_DISPLAY = display

    return PYARMOR_BIN


def vendor_dependencies():
    """依存パッケージを_vendorフォルダにコピー"""
    # vendorディレクトリ（ビルド用一時フォルダ）
    vendor_dir = SRC_DIR.parent / ".build_vendor"

    # vendorディレクトリをクリーンアップ
    if vendor_dir.exists():
        print(f"🧹 既存の {vendor_dir} を削除します...")
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
    temp_dir = SRC_DIR.parent / ".temp_vendor"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(exist_ok=True)

    print("📦 依存パッケージをダウンロード中...")

    # 32bit Python用にパッケージをダウンロード
    import platform as plat

    arch = plat.architecture()[0]  # '32bit' or '64bit'
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    if arch == "32bit":
        # 32bit環境: 明示的に win32 パッケージを指定
        print(f"  ℹ️  32bit Python {python_version} 用のパッケージをダウンロードします")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                str(temp_dir),
                "--platform",
                "win32",
                "--python-version",
                python_version,
                "--only-binary=:all:",
                "--no-deps",
                "pycryptodome>=3.21.0",
            ],
            check=True,
        )
        # requests とその依存関係（pure Python）
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                str(temp_dir),
                "requests>=2.32.3,<3.0.0",
            ],
            check=True,
        )
    else:
        # 64bit環境: 通常通りインストール
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
    print("📋 パッケージをvendorフォルダにコピー中...")
    for dep in dependencies:
        src_path = temp_dir / dep
        if src_path.exists():
            dst_path = vendor_dir / dep
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
                print(f"  ✓ コピー完了: {dep}")
            else:
                print(f"  ⚠ スキップ（ディレクトリではない）: {dep}")
        else:
            print(f"  ⚠ 警告: {dep} が見つかりません")

    # .dist-infoや__pycache__などを削除
    print("🧹 不要なファイルをクリーンアップ中...")
    for item in vendor_dir.rglob("*"):
        if item.is_dir():
            if item.name in ["__pycache__", "tests", "test"]:
                shutil.rmtree(item)
            elif item.suffix in [".dist-info", ".egg-info"]:
                shutil.rmtree(item)

    # 一時ディレクトリを削除
    shutil.rmtree(temp_dir)

    print(f"✅ vendoring完了: {vendor_dir}\n")
    return vendor_dir


def obfuscate_with_pyarmor():
    """PyArmorでwinactor_for_wmcを暗号化（_vendorは別途ビルドフォルダに作成）"""
    print("🔐 PyArmorで暗号化を実行中...")

    wmc_src = SRC_DIR / "winactor_for_wmc"
    if not wmc_src.exists():
        print("  ⚠ winactor_for_wmcが見つかりません。スキップします。")
        return

    pyarmor_cmd = get_pyarmor_command()
    if PYARMOR_CMD_DISPLAY:
        print(f"  ℹ️  PyArmorコマンド: {PYARMOR_CMD_DISPLAY}")

    # PyArmorで暗号化
    try:
        result = subprocess.run(
            pyarmor_cmd
            + [
                "gen",
                "-r",
                "--platform",
                "windows.x86",
                "-O",
                str(DEST_DIR),
                str(wmc_src),
            ],
            capture_output=True,
            text=True,
            cwd=str(SRC_DIR.parent),
        )

        # 出力を表示
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, result.args, result.stdout, result.stderr
            )

        print("  ✓ PyArmor暗号化完了")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ PyArmor暗号化エラー: {e}")
        raise


def copy_vendor_to_dest(vendor_src):
    """暗号化済みのディレクトリに_vendorをコピー"""
    vendor_dest = DEST_DIR / "winactor_for_wmc" / "_vendor"

    if vendor_src.exists():
        print("  📦 _vendorディレクトリをコピー中（暗号化なし）...")
        if vendor_dest.exists():
            shutil.rmtree(vendor_dest)
        shutil.copytree(vendor_src, vendor_dest)
        print("  ✓ _vendorコピー完了")


def main():
    # コピー先ディレクトリがなければ作成
    print("=" * 60)
    print("STEP 1: パッケージのコピー")
    print("=" * 60)
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

    # winactor_for_wmcは暗号化、それ以外は通常コピー
    for pkg in packages:
        dest_path = DEST_DIR / pkg.name

        if pkg.name == "winactor_for_wmc":
            # STEP 2: PyArmorで暗号化
            print("\n" + "=" * 60)
            print("STEP 2: PyArmorによる暗号化")
            print("=" * 60)

            # 暗号化前に出力先を完全にクリア（古い_vendorが残らないように）
            if dest_path.exists():
                print(f"🧹 既存の {dest_path} を削除します...")
                shutil.rmtree(dest_path)

            obfuscate_with_pyarmor()
        else:
            # 既存のコピー先があれば削除
            if dest_path.exists():
                print(f"🧹 既存の {dest_path} を削除します...")
                shutil.rmtree(dest_path)

            print(f"📦 {pkg.name} を {dest_path} にコピーします...")
            shutil.copytree(pkg, dest_path)

    # STEP 3: vendoring（暗号化後）
    print("\n" + "=" * 60)
    print("STEP 3: 依存パッケージのvendoring")
    print("=" * 60)
    vendor_dir = vendor_dependencies()

    # STEP 4: _vendorを暗号化済みディレクトリにコピー
    print("\n" + "=" * 60)
    print("STEP 4: _vendorを配置")
    print("=" * 60)
    copy_vendor_to_dest(vendor_dir)

    print("\n" + "=" * 60)
    print("✅ 全ての処理が完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"❌ {exc}")
        sys.exit(1)
