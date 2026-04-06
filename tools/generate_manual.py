"""
tools/generate_manual.py

WinActor ノードのマニュアルサイトを自動生成するツール。

src/winactor_nodes/ 配下の各ノードフォルダを走査し、
script.py から入力変数・出力変数を抽出、comment.txt から概要情報を読み取り、
MkDocs 用の Markdown ファイル群と mkdocs.yml を生成する。

--build オプションを指定すると mkdocs build + ZIP パッケージングを行い、
配布用の ZIP ファイルを生成する。

使用例:
 python tools/generate_manual.py          # Markdown と mkdocs.yml を生成
 python tools/generate_manual.py --clean  # docs/nodes/ を削除してから再生成
 python tools/generate_manual.py --build  # 上記 + mkdocs build + ZIP 出力
"""

import argparse
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
WINACTOR_NODES_DIR = REPO_ROOT / "src" / "winactor_nodes"
DOCS_DIR = REPO_ROOT / "docs"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
SITE_DIR = REPO_ROOT / "site"


# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------


@dataclass
class VarInfo:
    """1 つの変数の情報。"""

    name: str
    required: bool
    description: str
    direction: str = ""  # "input" or "output"


@dataclass
class NodeInfo:
    """1 つの WinActor ノードの情報。"""

    category: str
    name: str
    description: str
    version: str
    variables: list[VarInfo] = field(default_factory=list)


# ---------------------------------------------------------------------------
# ファイル読み取りユーティリティ
# ---------------------------------------------------------------------------


def _read_text_any_encoding(path: Path) -> str:
    """UTF-8 (BOM 付き含む) → Shift-JIS の順でテキストを読み取る。"""
    for enc in ("utf-8-sig", "shift_jis", "cp932"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# comment.txt パーサー（■ / [] 形式）
# ---------------------------------------------------------------------------


def _clean_indent(text: str) -> str:
    """全角スペースのインデントを除去し、copyright 行を除去する。"""
    text = re.sub(r"^[　]+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\(c\).*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()


def _parse_variables(settings_text: str) -> list[VarInfo]:
    """■設定項目 セクション内の [\\*変数名] / [変数名] ブロックをパースする。"""
    variables: list[VarInfo] = []
    pattern = re.compile(r"^\[(\*?)([^\]]+)\]", re.MULTILINE)
    matches = list(pattern.finditer(settings_text))

    for i, m in enumerate(matches):
        required = m.group(1) == "*"
        name = m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(settings_text)
        desc = _clean_indent(settings_text[start:end])
        variables.append(VarInfo(name=name, required=required, description=desc))

    return variables


def parse_comment_txt(comment_path: Path) -> tuple[str, str, list[VarInfo]]:
    """comment.txt から機能概要・バージョン・変数情報を抽出する。"""
    if not comment_path.exists():
        return ("（comment.txt なし）", "不明", [])

    text = _read_text_any_encoding(comment_path)

    # ■機能概要
    desc_match = re.search(
        r"■機能概要\s*\n(.*?)(?=^■|\Z)", text, re.DOTALL | re.MULTILINE
    )
    description = _clean_indent(desc_match.group(1)) if desc_match else ""

    # ■バージョン
    ver_match = re.search(
        r"■バージョン\s*\n(.*?)(?=^■|\Z)", text, re.DOTALL | re.MULTILINE
    )
    version = "不明"
    if ver_match:
        ver_text = _clean_indent(ver_match.group(1))
        if ver_text:
            version = ver_text.splitlines()[0].strip()

    # ■設定項目
    settings_match = re.search(
        r"■設定項目[^\n]*\n(.*?)(?=^■|\Z)", text, re.DOTALL | re.MULTILINE
    )
    variables: list[VarInfo] = []
    if settings_match:
        variables = _parse_variables(settings_match.group(1))

    return (description or "（概要なし）", version, variables)


# ---------------------------------------------------------------------------
# script.py パーサー
# ---------------------------------------------------------------------------


def parse_script_py(script_path: Path) -> tuple[list[str], list[str]]:
    """script.py から入力変数 (!var!) と出力変数 ($var$) を抽出する。"""
    if not script_path.exists():
        return ([], [])

    text = _read_text_any_encoding(script_path)

    input_vars_raw = re.findall(r"!([^!]+)!", text)
    input_vars = list(dict.fromkeys(v.split("|")[0] for v in input_vars_raw))

    output_names_raw = re.findall(r"winactor\.set_variable\(\$([^$]+)\$", text)
    output_vars = list(dict.fromkeys(v.split("|")[0] for v in output_names_raw))

    return (input_vars, output_vars)


# ---------------------------------------------------------------------------
# ノード収集
# ---------------------------------------------------------------------------


def collect_nodes(nodes_dir: Path) -> list[NodeInfo]:
    """winactor_nodes/ 配下のノード情報を収集する。"""
    if not nodes_dir.exists():
        return []

    nodes: list[NodeInfo] = []

    categories = sorted(
        [d for d in nodes_dir.iterdir() if d.is_dir()], key=lambda d: d.name
    )

    for category_dir in categories:
        node_dirs = sorted(
            [d for d in category_dir.iterdir() if d.is_dir()], key=lambda d: d.name
        )

        for node_dir in node_dirs:
            script_path = node_dir / "script.py"
            comment_path = node_dir / "comment.txt"

            description, version, variables = parse_comment_txt(comment_path)
            input_vars, output_vars = parse_script_py(script_path)

            for var in variables:
                if var.name in input_vars:
                    var.direction = "input"
                elif var.name in output_vars:
                    var.direction = "output"
                else:
                    var.direction = "input" if var.required else "output"

            nodes.append(
                NodeInfo(
                    category=category_dir.name,
                    name=node_dir.name,
                    description=description,
                    version=version,
                    variables=variables,
                )
            )

    return nodes


# ---------------------------------------------------------------------------
# Markdown 生成
# ---------------------------------------------------------------------------


def _escape_for_table(text: str, *, br: bool = False) -> str:
    """Markdown テーブルセル内で安全な文字列にする。"""
    text = text.replace("|", "\\|")
    text = text.replace("\n", "<br>" if br else " ")
    return text


def _version_badge(version: str) -> str:
    v = version.replace("-", "--").replace(" ", "_")
    return f"![version](https://img.shields.io/badge/version-{v}-blue)"


def generate_node_markdown(node: NodeInfo) -> str:
    """1 つのノードの Markdown ページを生成する。"""
    lines: list[str] = []

    lines.append(f"# {node.name}")
    lines.append("")

    lines.append(_version_badge(node.version))
    lines.append("")

    lines.append("## 概要")
    lines.append("")

    lines.append(node.description)
    lines.append("")

    input_vars = [v for v in node.variables if v.direction == "input"]
    output_vars = [v for v in node.variables if v.direction == "output"]

    # 設定値
    lines.append("## 設定値")
    lines.append("")

    if input_vars:
        lines.append("| 変数名 | 説明 |")
        lines.append("|--------|------|")
        for var in input_vars:
            req = " ***\\****" if var.required else ""
            desc = _escape_for_table(var.description, br=True)
            lines.append(f"| `{var.name}`{req} | {desc} |")
        lines.append("")
    else:
        lines.append("!!! info")
        lines.append("    設定値はありません。")
        lines.append("")

    # 戻り値
    lines.append("## 戻り値")
    lines.append("")

    if output_vars:
        lines.append("| 変数名 | 説明 |")
        lines.append("|--------|------|")
        for var in output_vars:
            desc = _escape_for_table(var.description, br=True)
            lines.append(f"| `{var.name}` | {desc} |")
        lines.append("")
    else:
        lines.append("!!! info")
        lines.append("    戻り値はありません。")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_index_markdown(nodes: list[NodeInfo]) -> str:
    """トップページ（ノード一覧）の Markdown を生成する。"""
    lines: list[str] = []
    lines.append("# WinActor ノード一覧")
    lines.append("")

    if not nodes:
        lines.append("ノードが見つかりません。")
        return "\n".join(lines) + "\n"

    categories: dict[str, list[NodeInfo]] = {}
    for node in nodes:
        categories.setdefault(node.category, []).append(node)

    lines.append(f"全 **{len(nodes)}** ノード / **{len(categories)}** カテゴリ")
    lines.append("")

    for cat_name, cat_nodes in categories.items():
        lines.append(f"## {cat_name}")
        lines.append("")

        lines.append(f"*{len(cat_nodes)} ノード*")
        lines.append("")

        lines.append("| ノード名 | 概要 |")
        lines.append("|----------|------|")

        for node in cat_nodes:
            md_path = f"nodes/{node.category}/{node.name}.md"
            desc = _escape_for_table(node.description)
            lines.append(f"| [{node.name}]({md_path}) | {desc} |")

        lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# mkdocs.yml 生成
# ---------------------------------------------------------------------------


def get_site_name() -> str:
    """pyproject.toml の [tool.manual] site-name を取得する。"""
    default = "WinActor ノード マニュアル"
    if not PYPROJECT.exists():
        return default

    text = PYPROJECT.read_text(encoding="utf-8")

    match = re.search(
        r"\[tool\.manual\].*?site-name\s*=\s*\"([^\"]+)\"", text, re.DOTALL
    )
    if match:
        return match.group(1)

    match = re.search(r'^description\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if match:
        return match.group(1)

    return default


def get_static_pages() -> list[dict[str, str]]:
    """pyproject.toml の [tool.manual] pages から固定ページ一覧を取得する。"""
    if not PYPROJECT.exists():
        return []

    text = PYPROJECT.read_text(encoding="utf-8")
    if "[tool.manual]" not in text:
        return []

    pages_match = re.search(
        r"\[tool\.manual\].*?pages\s*=\s*\[\s*\n(.*?)\]", text, re.DOTALL
    )
    if not pages_match:
        return []

    pages = []
    for line in pages_match.group(1).splitlines():
        line = line.strip().rstrip(",")
        if not line or line.startswith("#"):
            continue

        title_match = re.search(r'title\s*=\s*"([^"]+)"', line)
        path_match = re.search(r'path\s*=\s*"([^"]+)"', line)
        section_match = re.search(r'section\s*=\s*"([^"]+)"', line)

        if title_match and path_match:
            page: dict[str, str] = {
                "title": title_match.group(1),
                "path": path_match.group(1),
            }
            if section_match:
                page["section"] = section_match.group(1)
            pages.append(page)

    return pages


def build_nav(
    static_pages: list[dict[str, str]], nodes: list[NodeInfo]
) -> list:
    """mkdocs.yml の nav 構造を生成する。"""
    nav: list = []

    # はじめに（トップページ）
    nav.append({"はじめに": "index.md"})

    # 固定ページ → section でグループ化
    sections: dict[str, list] = {}

    for page in static_pages:
        if "section" in page:
            sections.setdefault(page["section"], []).append(
                {page["title"]: page["path"]}
            )
        else:
            nav.append({page["title"]: page["path"]})

    # section をトップレベルに挿入（出現順を維持）
    # navigation.indexes 対応: setup/index.md があればセクションの index ページにする
    seen_sections: set[str] = set()
    for page in static_pages:
        if "section" in page:
            sec = page["section"]
            if sec not in seen_sections:
                seen_sections.add(sec)
                section_items: list = []
                # セクション index ページを検出して先頭に配置
                # section 内の全ページからディレクトリを収集し、共通の index.md を探す
                sec_dirs = {
                    str(Path(p["path"]).parent)
                    for p in static_pages
                    if p.get("section") == sec
                }
                index_path = None
                for d in sorted(sec_dirs):
                    candidate = f"{d}/index.md"
                    if (DOCS_DIR / candidate).exists():
                        index_path = candidate
                        break
                index_file = DOCS_DIR / index_path if index_path else None
                if index_file is not None and index_file.exists():
                    section_items.append({sec: index_path})
                section_items.extend(sections[sec])
                nav.append({sec: section_items})

    # ノードリファレンス
    categories: dict[str, list[dict[str, str]]] = {}
    for node in nodes:
        if node.category not in categories:
            categories[node.category] = []
        categories[node.category].append(
            {node.name: f"nodes/{node.category}/{node.name}.md"}
        )

    node_items: list = [{"ノード一覧": "node-list.md"}]
    for cat_name, cat_nodes in categories.items():
        node_items.append({cat_name: cat_nodes})

    if nodes:
        nav.append({"ノードリファレンス": node_items})
    elif (DOCS_DIR / "node-list.md").exists():
        nav.append({"ノードリファレンス": [{"ノード一覧": "node-list.md"}]})

    return nav


def generate_mkdocs_yml(nav: list, site_name: str) -> str:
    """mkdocs.yml の内容を生成する。"""
    config = {
        "site_name": site_name,
        "use_directory_urls": False,
        "theme": {
            "name": "material",
            "language": "ja",
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": "red",
                    "accent": "red",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "ダークモードに切り替え",
                    },
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": "red",
                    "accent": "red",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "ライトモードに切り替え",
                    },
                },
            ],
            "font": {
                "text": "Noto Sans JP",
                "code": "JetBrains Mono",
            },
            "icon": {
                "repo": "fontawesome/brands/github",
            },
            "features": [
                "navigation.instant",
                "navigation.instant.prefetch",
                "navigation.instant.progress",
                "navigation.tracking",
                "navigation.tabs",
                "navigation.tabs.sticky",
                "navigation.sections",
                "navigation.top",
                "navigation.footer",
                "navigation.indexes",
                "toc.follow",
                "search.suggest",
                "search.highlight",
                "content.code.copy",
                "content.tabs.link",
            ],
        },
        "plugins": [
            "offline",
            {
                "search": {
                    "separator": r"[\s\u200b\-_,:!=\[\]()\"\`/]+|"
                    r"\.(?!\d)|&[lg]t;|(?!\b)(?=[A-Z][a-z])"
                }
            },
        ],
        "markdown_extensions": [
            "admonition",
            "pymdownx.details",
            "pymdownx.superfences",
            {"pymdownx.highlight": {"anchor_linenums": True}},
            "pymdownx.inlinehilite",
            "attr_list",
            "md_in_html",
            {"toc": {"permalink": True}},
            "pymdownx.emoji",
            {"pymdownx.tabbed": {"alternate_style": True}},
            {"pymdownx.tasklist": {"custom_checkbox": True}},
        ],
        "copyright": "&copy; 丸紅情報システムズ",
        "extra_css": [
            "stylesheets/extra.css",
        ],
        "extra": {
            "generator": False,
        },
        "nav": nav,
    }

    raw = yaml.dump(
        config, allow_unicode=True, default_flow_style=False, sort_keys=False
    )

    # pymdownx.emoji を !!python/name タグ付きに置換
    raw = raw.replace(
        "- pymdownx.emoji\n",
        "- pymdownx.emoji:\n"
        "    emoji_index: !!python/name:material.extensions.emoji.twemoji\n"
        "    emoji_generator: !!python/name:material.extensions.emoji.to_svg\n",
    )

    return raw


# ---------------------------------------------------------------------------
# ドキュメント書き出し
# ---------------------------------------------------------------------------


def write_docs(
    nodes: list[NodeInfo],
    static_pages: list[dict[str, str]],
    site_name: str,
) -> None:
    """Markdown ファイル群と mkdocs.yml を書き出す。"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 固定ページの存在チェック
    for page in static_pages:
        page_path = DOCS_DIR / page["path"]
        if page["path"] != "index.md" and not page_path.exists():
            page_path.parent.mkdir(parents=True, exist_ok=True)
            page_path.write_text(
                f"# {page['title']}\n\n（このページは自動生成されたテンプレートです。"
                "内容を編集してください。）\n",
                encoding="utf-8",
            )
            print(f"[INFO] 固定ページのテンプレートを生成: {page_path}")

    # docs/node-list.md（自動生成のノード一覧ページ）
    node_list_path = DOCS_DIR / "node-list.md"
    node_list_path.write_text(generate_index_markdown(nodes), encoding="utf-8")

    # docs/nodes/{category}/{node_name}.md
    for node in nodes:
        node_path = DOCS_DIR / "nodes" / node.category / f"{node.name}.md"
        node_path.parent.mkdir(parents=True, exist_ok=True)
        node_path.write_text(generate_node_markdown(node), encoding="utf-8")

    # docs/stylesheets/extra.css
    css_dir = DOCS_DIR / "stylesheets"
    css_dir.mkdir(parents=True, exist_ok=True)
    css_path = css_dir / "extra.css"
    if not css_path.exists():
        css_path.write_text(_EXTRA_CSS, encoding="utf-8")

    # mkdocs.yml
    nav = build_nav(static_pages, nodes)
    MKDOCS_YML.write_text(generate_mkdocs_yml(nav, site_name), encoding="utf-8")


# ---------------------------------------------------------------------------
# ビルド & ZIP パッケージング
# ---------------------------------------------------------------------------


def build_and_package(output_path: Path) -> None:
    """
    mkdocs build を実行し、site/ を ZIP にパッケージングする。

    offline プラグインにより file:// でも動作するサイトが生成される。
    ユーザーは ZIP を解凍して index.html を開くだけで利用可能。
    """
    print("[INFO] mkdocs build を実行中...")
    result = subprocess.run(
        ["mkdocs", "build", "--strict"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[ERROR] mkdocs build が失敗しました:\n{result.stderr}")
        raise SystemExit(1)

    if not SITE_DIR.exists():
        print(f"[ERROR] site/ が見つかりません: {SITE_DIR}")
        raise SystemExit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ZIP 構造:
    # index.html ← リダイレクト用（これだけトップに見える）
    # _site/ ← MkDocs サイト一式
    #   index.html
    #   assets/
    #   nodes/
    #   ...

    site_prefix = "_site"

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # サイト本体を _site/ 配下に格納
        for file in sorted(SITE_DIR.rglob("*")):
            if file.is_file():
                arcname = f"{site_prefix}/{file.relative_to(SITE_DIR)}"
                zf.write(file, arcname)

        # トップに置くリダイレクト用 index.html
        zf.writestr("index.html", _REDIRECT_HTML)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[INFO] ZIP を生成しました: {output_path} ({size_mb:.1f} MB)")


# ---------------------------------------------------------------------------
# リダイレクト用 HTML
# ---------------------------------------------------------------------------

_REDIRECT_HTML = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=_site/index.html">
<title>マニュアルを開いています...</title>
</head>
<body>
<p>自動で開かない場合は <a href="_site/index.html">こちら</a> をクリックしてください。</p>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# extra.css
# ---------------------------------------------------------------------------

_EXTRA_CSS = """\
/* WinActor Node Manual — Corporate Theme */

.md-typeset h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.md-typeset h2 {
    font-size: 1.2rem;
    font-weight: 600;
}

.md-typeset h3 {
    font-weight: 600;
}

.md-typeset table:not([class]) {
    border-radius: 8px;
    overflow: hidden;
    border-collapse: separate;
    border-spacing: 0;
    display: table;
    width: 100%;
    max-width: 800px;
    table-layout: fixed;
}

.md-typeset table:not([class]) th:first-child,
.md-typeset table:not([class]) td:first-child {
    width: 180px;
}

.md-typeset table:not([class]) th {
    font-weight: 600;
    text-transform: none;
    letter-spacing: 0;
}

.md-typeset table:not([class]) tbody tr {
    transition: background 0.1s ease;
}

[data-md-color-scheme="default"] .md-typeset table:not([class]) tbody tr:hover {
    background: rgba(0, 0, 0, 0.02);
}

[data-md-color-scheme="slate"] .md-typeset table:not([class]) tbody tr:hover {
    background: rgba(255, 255, 255, 0.02);
}

.md-typeset pre {
    border-radius: 8px;
}

.md-typeset .admonition,
.md-typeset details {
    border-radius: 8px;
}

.md-footer__title {
    font-weight: 600;
}

.md-footer__direction {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.md-copyright {
    font-size: 0.68rem;
    letter-spacing: 0.02em;
}

.md-content {
    min-height: calc(100vh - 8rem);
}

.md-sidebar {
    position: sticky;
    top: 4.8rem;
    height: calc(100vh - 4.8rem);
    overflow: hidden;
}

.md-sidebar__scrollwrap {
    max-height: 100%;
    overflow-y: auto;
}

.md-grid {
    max-width: 1220px;
}
"""


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="WinActor ノードの MkDocs マニュアルサイトを自動生成する"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="docs/nodes/ を削除してから再生成する（固定ページは保持）",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="mkdocs build を実行し、配布用 ZIP を生成する",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO_ROOT / "dist" / "manual.zip",
        help="ZIP の出力先 (--build 時のみ有効)",
    )
    parser.add_argument(
        "--nodes-dir",
        type=Path,
        default=WINACTOR_NODES_DIR,
        help="ノードディレクトリのパス",
    )
    args = parser.parse_args()

    # --clean は docs/nodes/ のみ削除
    nodes_out = DOCS_DIR / "nodes"
    if args.clean and nodes_out.exists():
        shutil.rmtree(nodes_out)
        print(f"[INFO] {nodes_out} を削除しました。")

    nodes = collect_nodes(args.nodes_dir)
    static_pages = get_static_pages()
    site_name = get_site_name()

    write_docs(nodes, static_pages, site_name)
    print(f"[INFO] マニュアルを生成しました: {DOCS_DIR}")
    print(f"[INFO] ノード数: {len(nodes)}")
    print(f"[INFO] 固定ページ数: {len(static_pages)}")
    print(f"[INFO] mkdocs.yml: {MKDOCS_YML}")

    if args.build:
        build_and_package(args.output)
    else:
        print("")
        print("次のステップ:")
        print("  mkdocs serve          # プレビュー (http://localhost:8000)")
        print("  mkdocs build          # site/ に静的サイトを生成")
        print("  python -m tools.generate_manual --build  # 配布用 ZIP を生成")
        print("  python -m tools       # ランチャーメニュー")


if __name__ == "__main__":
    main()
