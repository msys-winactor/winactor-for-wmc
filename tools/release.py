import argparse
import subprocess
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
BIN_DIR = REPO_ROOT / "bin" / "winactor_nodes"
DIST_DIR = REPO_ROOT / "dist"


def get_repo_name() -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True,
    )
    url = result.stdout.strip()
    return Path(url.rstrip(".git")).stem


def get_latest_version() -> str:
    result = subprocess.run(["git", "tag"], capture_output=True, text=True, check=True)
    tags = [
        tag.lstrip("v")
        for tag in result.stdout.strip().splitlines()
        if tag.startswith("v")
    ]
    if not tags:
        return "0.0.0"
    return sorted(tags, key=lambda s: list(map(int, s.split("."))))[-1]


def bump_version(version: str, part: str) -> str:
    major, minor, patch = map(int, version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("Invalid bump type")


def set_version_in_pyproject(version: str):
    lines = PYPROJECT.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("version"):
            new_lines.append(f'version = "{version}"')
        else:
            new_lines.append(line)
    PYPROJECT.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"[INFO] Updated pyproject.toml to version {version}.")


def create_zip(repo_name: str, version: str):
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"{repo_name}-v{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in BIN_DIR.rglob("*"):
            if path.is_file():
                arcname = path.relative_to(BIN_DIR.parent)
                zipf.write(path, arcname)
    print(f"[INFO] Created ZIP archive: {zip_path}")


def create_git_tag(version: str):
    subprocess.run(["git", "add", "pyproject.toml"])
    subprocess.run(["git", "commit", "-m", f"Bump version to {version}"])
    subprocess.run(["git", "tag", f"v{version}"])
    subprocess.run(["git", "push"])
    subprocess.run(["git", "push", "--tags"])
    print(f"[INFO] Created and pushed Git tag v{version}.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        required=True,
        help="Which part of the version to bump",
    )
    parser.add_argument(
        "--tag", action="store_true", help="Also create and push a Git tag"
    )
    args = parser.parse_args()

    repo = get_repo_name()
    current = get_latest_version()
    new_version = bump_version(current, args.bump)

    print(f"[INFO] Bumping version: v{current} -> v{new_version}")
    set_version_in_pyproject(new_version)
    create_zip(repo, new_version)

    if args.tag:
        create_git_tag(new_version)


if __name__ == "__main__":
    main()
