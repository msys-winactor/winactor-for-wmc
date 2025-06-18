# Template Python

## 📖 概要

このリポジトリは、Python を使用したテンプレートプロジェクトです。

---

## 📁 フォルダ構成

```
.
├── src/
│   ├── template_python/         # パッケージ実装（フォルダ名はプロジェクトに合わせて変更）
│   └── winactor_nodes/          # WinActorノード用スクリプト（パッケージ外）
│
├── tests/                       # pytest用テストスクリプト
├── tools/
│   ├── package_copy_to_public.py  # パッケージ配置スクリプト
│   └── release.py               # バージョン更新 + ZIPリリース作成スクリプト
├── pyproject.toml               # Poetry設定
└── README.md                    # 本ドキュメント
```

---

## 🛠 主な機能

- **パッケージ**

  - `src/template_python`

- **WinActor ノード操作**

  - `src/winactor_nodes`

---

## ✅ テスト実行

テストコードは `pytest` フレームワークを利用します。

```powershell
poetry run pytest
```

---

## 💻 開発環境

- Python 3.12.4（固定バージョン）
- Poetry を使用した依存管理
- VSCode + flake8 / black / isort / pytest

---

## 🚀 プロジェクトのはじめかた（テンプレート利用）

このリポジトリをテンプレートとして使い、新しいプロジェクトを開始する手順です。

### 1. GitHub 上で新規リポジトリを作成

1. 以下のリンクを開く  
   👉 https://github.com/msys-winactor/template-python/generate
2. リポジトリ名を入力（例：`my-winactor-lib`）
3. 「Private」または「Public」を選択し、「Create repository from template」をクリック

### 2. ローカルにクローン

```powershell
git clone https://github.com/<ユーザー名>/<新しいリポジトリ名>.git
cd <新しいリポジトリ名>
```

### 3. Poetry 環境をセットアップ

```powershell
poetry install
```

### 4. パッケージ名の変更

- `src/template_python/` のフォルダ名をプロジェクト名に合わせて変更（例：`my_winactor_lib/`）
- `pyproject.toml` の `[tool.poetry] name` を変更：

```toml
[tool.poetry]
name = "my-winactor-lib"
```

### 5. パッケージを Public フォルダにコピー

```powershell
poetry run copy-to-public
```

以上で開発を開始できます！

---

## 📦 リリース手順

このプロジェクトには、`tools/release.py` によるリリースツールが含まれています。  
以下の手順で `bin/winactor_nodes/` フォルダを ZIP 形式でパッケージし、必要に応じて Git タグの作成・push まで実行できます。

### ✅ 実行方法

```powershell
python tools/release.py --bump [major|minor|patch] [--tag]
```

| オプション | 説明                                                                                                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--bump`   | バージョンの更新種別（必須）<br>`major`: メジャー更新（例: 1.0.0 → 2.0.0）<br>`minor`: マイナー更新（例: 1.2.3 → 1.3.0）<br>`patch`: パッチ更新（例: 1.2.3 → 1.2.4） |
| `--tag`    | `pyproject.toml`のバージョンを更新し commit + Git タグ`vX.Y.Z` を作成 + push                                                                                         |

---

### 🗂 出力内容

- ZIP ファイルは `dist/` フォルダに出力されます
- ファイル名：
  ```
  <リポジトリ名>-v<バージョン>.zip
  例: my-repo-v1.2.4.zip
  ```

---

### 🧪 使用例

```powershell
# パッチバージョンを更新して ZIP だけ作成
python tools/release.py --bump patch

# マイナーバージョンを更新して Git タグ付きで push も行う
python tools/release.py --bump minor --tag
```

---

### 📝 備考

- `pyproject.toml` の `version = "..."` は自動で上書きされます
- Git タグ `vX.Y.Z` は `git push` 済みになります（`--tag` 指定時）
- ZIP 作成対象：`bin/winactor_nodes` ディレクトリ配下すべて
