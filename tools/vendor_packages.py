"""
依存パッケージを _vendor/ にベンダリングするツール。

使い方:
    py -3.12-32 tools/vendor_packages.py          # 32bit (WinActor本番環境向け)
    py -3.12    tools/vendor_packages.py --64bit   # 64bit (動作確認用)

32bit モードの対象 Python バージョンは [tool.winactor] から取得する。
"""

import argparse
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"


def _load_pyproject() -> dict:
    """pyproject.toml を読み込んで返す。"""
    with PYPROJECT_TOML.open("rb") as f:
        return tomllib.load(f)


NATIVE_TRANSITIVE_DEPS = ["cffi", "pycparser"]


def _load_vendor_packages() -> list[str]:
    """pyproject.toml からベンダリング対象パッケージを返す（python は除外）。"""
    data = _load_pyproject()
    deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    packages = [name for name in deps if name.lower() != "python"]
    packages += NATIVE_TRANSITIVE_DEPS
    return packages


def _load_winactor_target() -> tuple[str, str]:
    """
    pyproject.toml の [tool.winactor] からターゲット Python バージョンと
    アーキテクチャを返す。(例: ("3.12", "32"))
    """
    data = _load_pyproject()
    winactor = data.get("tool", {}).get("winactor", {})
    py_ver = winactor.get("target-python", f"{sys.version_info.major}.{sys.version_info.minor}")
    arch = winactor.get("target-arch", "32")
    return py_ver, arch


# コピー不要なフォルダ／ファイルのパターン
EXCLUDE_PATTERNS = [
    "*.dist-info",
    "*.egg-info",
    "__pycache__",
    "tests",
    "test",
]

VENDOR_DIR = PROJECT_ROOT / "src" / "winactor_for_wmc" / "_vendor"


def _current_python_matches_target(py_ver: str, arch: str) -> bool:
    """実行中の Python がターゲットと一致するかチェック。"""
    current_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    current_bits = struct.calcsize("P") * 8
    target_bits = 32 if arch == "32" else 64
    return current_ver == py_ver and current_bits == target_bits


def pip_install(target: Path, is_32bit: bool) -> None:
    packages = _load_vendor_packages()
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--target", str(target),
        "--upgrade",
    ]
    if is_32bit:
        py_ver, arch = _load_winactor_target()
        if _current_python_matches_target(py_ver, arch):
            print(f"Running Python matches target ({py_ver}, {arch}bit) — skipping cross-compilation flags")
        else:
            abi_tag = f"cp{py_ver.replace('.', '')}"
            platform = "win32" if arch == "32" else "win_amd64"
            cmd += [
                "--platform", platform,
                "--python-version", py_ver,
                "--implementation", "cp",
                "--abi", abi_tag,
                "--only-binary=:all:",
            ]
            print(f"Cross-compile target: Python {py_ver} ({arch}bit, abi: {abi_tag})")
    cmd += packages
    print(f"Packages: {packages}")
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def matches_exclude(path: Path) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if path.match(pattern):
            return True
    return False


def copy_vendor(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if matches_exclude(item):
            print(f"  skip: {item.name}")
            continue
        dest_item = dst / item.name
        if item.is_dir():
            if dest_item.exists():
                shutil.rmtree(dest_item)
            shutil.copytree(item, dest_item)
            # コピー後に各サブディレクトリ内の除外対象も削除
            for pattern in EXCLUDE_PATTERNS:
                for match in dest_item.rglob(pattern):
                    if match.exists():
                        if match.is_dir():
                            shutil.rmtree(match)
                        else:
                            match.unlink()
        else:
            shutil.copy2(item, dest_item)
        print(f"  copied: {item.name}")


def _verify_vendor(vendor_dir: Path, is_32bit: bool) -> None:
    """ベンダリング後に必須ファイルの存在を確認する。"""
    errors: list[str] = []

    rust_candidates = list((vendor_dir / "cryptography" / "hazmat" / "bindings").glob("_rust*"))
    if not rust_candidates:
        errors.append("cryptography/hazmat/bindings/_rust*.pyd が見つかりません")
    else:
        print(f"  OK: cryptography/hazmat/bindings/{rust_candidates[0].name}")

    cffi_candidates = list(vendor_dir.glob("_cffi_backend*"))
    if not cffi_candidates:
        errors.append("_cffi_backend*.pyd が見つかりません")
    else:
        print(f"  OK: {cffi_candidates[0].name}")

    if is_32bit:
        crypto_libs = vendor_dir / "cryptography.libs"
        if crypto_libs.is_dir():
            dlls = list(crypto_libs.glob("*.dll"))
            print(f"  OK: cryptography.libs/ ({len(dlls)} DLLs)")
        else:
            print("  INFO: cryptography.libs/ not found (may be statically linked)")

    if errors:
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        raise RuntimeError("Vendoring verification failed: " + "; ".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser(description="Vendor dependencies into _vendor/")
    parser.add_argument("--64bit", dest="is_64bit", action="store_true",
                        help="64bitモードでインストール（動作確認用）")
    args = parser.parse_args()
    is_32bit = not args.is_64bit

    print(f"Mode: {'32bit (WinActor)' if is_32bit else '64bit (dev)'}")
    print(f"Vendor dir: {VENDOR_DIR}")

    if VENDOR_DIR.exists():
        print(f"Removing existing {VENDOR_DIR} ...")
        shutil.rmtree(VENDOR_DIR)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        print("\n--- pip install ---")
        pip_install(tmp_path, is_32bit)
        print("\n--- pip install result (native extensions) ---")
        for f in sorted(tmp_path.rglob("*.pyd")):
            print(f"  {f.relative_to(tmp_path)}")
        for f in sorted(tmp_path.rglob("*.dll")):
            print(f"  {f.relative_to(tmp_path)}")
        cffi_check = list(tmp_path.glob("_cffi_backend*"))
        if cffi_check:
            print(f"  _cffi_backend found: {cffi_check[0].name}")
        else:
            print("  WARNING: _cffi_backend NOT found in pip output!")
        print("\n--- copy to _vendor/ ---")
        copy_vendor(tmp_path, VENDOR_DIR)

    print("\n--- verify vendored packages ---")
    _verify_vendor(VENDOR_DIR, is_32bit)

    print(f"\nDone. Packages vendored to: {VENDOR_DIR}")


if __name__ == "__main__":
    main()
