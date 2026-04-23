"""
tools/package_copy_to_public.py

src/ 配下のパッケージを PyArmor で暗号化して Public の配布先ディレクトリに配置するツール。
_vendor/ は暗号化せず、暗号化済みパッケージに別途コピーする。

使い方:
    py -3.12-32 tools/package_copy_to_public.py           # 32bit (WinActor本番環境向け)
    py -3.12    tools/package_copy_to_public.py --64bit   # 64bit (動作確認用)
    py -3.12-32 tools/package_copy_to_public.py --skip-vendor  # vendoring をスキップ
    poetry run python -m tools.package_copy_to_public --no-pyarmor  # 暗号化なし（開発用）
"""

import argparse
import codecs
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

# Windows の標準出力を UTF-8 に固定
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
DEST_DIR = Path(r"C:\Users\Public\msys-winactor-adapters\libs")
VENDOR_SCRIPT = Path(__file__).resolve().parent / "vendor_packages.py"
PYPROJECT_TOML = Path(__file__).resolve().parent.parent / "pyproject.toml"
EXCLUDE_DIRS = {"winactor_nodes"}


def _load_pyarmor_py_tag() -> str:
    """
    PyArmor 用の Python タグを返す（例: "-3.12-32"）。
    環境変数 PYARMOR_PY_TAG > pyproject.toml [tool.winactor] の順で取得。
    """
    env = os.environ.get("PYARMOR_PY_TAG")
    if env:
        return env
    with PYPROJECT_TOML.open("rb") as f:
        data = tomllib.load(f)
    winactor = data.get("tool", {}).get("winactor", {})
    py_ver = winactor.get("target-python", f"{sys.version_info.major}.{sys.version_info.minor}")
    arch = winactor.get("target-arch", "32")
    return f"-{py_ver}-{arch}"


_PYARMOR_PY_TAG = _load_pyarmor_py_tag()


# ── PyArmor コマンド解決 ───────────────────────────────────────────────────────


def _check_command(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def resolve_pyarmor_command() -> list[str]:
    """
    環境変数 PYARMOR_CMD があればそれを使う。
    なければ py {_PYARMOR_PY_TAG} -m pyarmor.cli.__main__ を探す。
    """
    env_cmd = os.environ.get("PYARMOR_CMD")
    if env_cmd:
        return shlex.split(env_cmd, posix=False)

    if not _check_command(["py", _PYARMOR_PY_TAG, "-c", "import sys"]):
        raise RuntimeError(
            f"WinActor と同じ 32bit Python (py {_PYARMOR_PY_TAG}) が見つかりません。\n"
            "  https://www.python.org/downloads/windows/ から 32bit Python をインストールするか、\n"
            "  環境変数 PYARMOR_CMD で PyArmor 実行コマンドを指定してください。"
        )

    cmd = ["py", _PYARMOR_PY_TAG, "-m", "pyarmor.cli.__main__"]
    if not _check_command(cmd + ["--version"]):
        raise RuntimeError(
            f"Python {_PYARMOR_PY_TAG} に PyArmor がインストールされていません。\n"
            f"  次を実行してください: py {_PYARMOR_PY_TAG} -m pip install pyarmor==9.2.3"
        )

    return cmd


# ── ステップ関数 ───────────────────────────────────────────────────────────────


def run_vendoring(is_32bit: bool) -> None:
    """vendor_packages.py を実行して _vendor/ を最新化する。"""
    cmd = [sys.executable, str(VENDOR_SCRIPT)]
    if not is_32bit:
        cmd.append("--64bit")
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def obfuscate_with_pyarmor(pkg_src: Path) -> None:
    """
    PyArmor で pkg_src を暗号化して DEST_DIR に出力する。
    _vendor/ は --exclude で除外する。
    """
    pyarmor_cmd = resolve_pyarmor_command()
    print(f"PyArmor: {' '.join(pyarmor_cmd)}")

    cmd = pyarmor_cmd + [
        "gen",
        "-r",
        "--platform", "windows.x86",
        "--exclude", "_vendor",
        "-O", str(DEST_DIR),
        str(pkg_src),
    ]
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SRC_DIR.parent))
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    result.check_returncode()


def copy_package_plain(pkg_src: Path) -> None:
    """
    PyArmor を使わずに pkg_src をそのまま DEST_DIR にコピーする。
    """
    dest = DEST_DIR / pkg_src.name
    print(f"Copying:  {pkg_src} -> {dest}")
    shutil.copytree(pkg_src, dest)


def copy_vendor_to_dest(pkg_src: Path) -> None:
    """
    pkg_src/_vendor/ を DEST_DIR/{pkg_src.name}/_vendor/ にコピーする。
    _vendor/ が存在しない場合はスキップする。
    """
    vendor_src = pkg_src / "_vendor"
    if not vendor_src.exists():
        print(f"  _vendor/ not found in {pkg_src}, skipping.")
        return

    vendor_dest = DEST_DIR / pkg_src.name / "_vendor"
    if vendor_dest.exists():
        shutil.rmtree(vendor_dest)
    print(f"Copying:  {vendor_src} -> {vendor_dest}")
    shutil.copytree(vendor_src, vendor_dest)


# ── エントリポイント ──────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="パッケージを PyArmor で暗号化して Public ディレクトリへ配置する"
    )
    parser.add_argument(
        "--64bit",
        dest="is_64bit",
        action="store_true",
        help="64bit モードでインストール（動作確認用）",
    )
    parser.add_argument(
        "--skip-vendor",
        action="store_true",
        help="_vendor/ が最新の場合に vendoring をスキップする",
    )
    parser.add_argument(
        "--no-pyarmor",
        action="store_true",
        help="PyArmor 暗号化をせずにそのままコピーする（開発用）",
    )
    args = parser.parse_args()
    is_32bit = not args.is_64bit

    packages = [
        d
        for d in SRC_DIR.iterdir()
        if d.is_dir() and (d / "__init__.py").exists() and d.name not in EXCLUDE_DIRS
    ]
    if not packages:
        print("Error: コピー対象のパッケージが見つかりません。", file=sys.stderr)
        sys.exit(1)

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_vendor:
        print("--- STEP 1: vendoring ---")
        run_vendoring(is_32bit)
        print()

    for pkg in packages:
        dest_pkg = DEST_DIR / pkg.name
        if dest_pkg.exists():
            print(f"Removing: {dest_pkg}")
            shutil.rmtree(dest_pkg)

        if args.no_pyarmor:
            print(f"--- STEP 2: copy ({pkg.name}) ---")
            copy_package_plain(pkg)
        else:
            print(f"--- STEP 2: PyArmor ({pkg.name}) ---")
            obfuscate_with_pyarmor(pkg)
        print()

        if not args.no_pyarmor:
            print(f"--- STEP 3: copy _vendor/ ({pkg.name}) ---")
            copy_vendor_to_dest(pkg)
            print()


    print(f"Done. Destination: {DEST_DIR}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
