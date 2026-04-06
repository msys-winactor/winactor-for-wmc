# WinActor for WMC

## 概要

WinActor Manager on Cloud（WMC）の API（v1.2）をラップし、WinActor から WMC を操作するための Python ライブラリです。  
10 カテゴリ・53 種類の WinActor ノードを提供し、RPA ワークフローから WMC の各種リソースを管理できます。

---

## 動作要件

- Windows 11 以降
- WinActor 7.6 以降
- Python 3.12.8（32bit）
- WinActor Manager on Cloud Ver. 3.8 以降

---

## フォルダ構成

```
.
├── src/
│   ├── winactor_for_wmc/          # メインパッケージ（WMC API ラッパー）
│   │   ├── auth/                  # 認証（トークン取得）
│   │   ├── common/                # 共通ユーティリティ（API クライアント、暗号化、ライセンス検証）
│   │   ├── schedules/             # スケジュール管理
│   │   ├── users/                 # ユーザ管理
│   │   ├── departments/           # 所属管理
│   │   ├── winactors/             # WinActor 管理
│   │   ├── scenarios/             # シナリオ管理
│   │   ├── tasks/                 # タスク管理
│   │   ├── files/                 # ファイル管理
│   │   ├── licenses/              # ライセンス管理
│   │   ├── events/                # イベントログ
│   │   └── statistics/            # 利用統計
│   │
│   └── winactor_nodes/            # WinActor ノード用スクリプト（53 ノード）
│
├── tests/                         # pytest テスト
├── tools/                         # 開発ツール
│   ├── package_copy_to_public.py  # パッケージ配置スクリプト
│   ├── release.py                 # バージョン更新 + ZIP リリース作成
│   ├── vendor_packages.py         # 依存パッケージのベンダリング
│   └── generate_manual.py         # MkDocs マニュアル自動生成
├── installer/                     # InnoSetup インストーラ定義
├── docs/                          # MkDocs ドキュメントソース
├── pyproject.toml                 # Poetry 設定
└── README.md                      # 本ドキュメント
```

---

## 提供ノード一覧

| カテゴリ | ノード数 | 主な操作 |
|---|---|---|
| 01\_認証関連 | 1 | アクセストークン取得 |
| 02\_WinActor関連 | 5 | 情報エクスポート、更新、削除、再起動、利用状況エクスポート |
| 03\_ライセンス関連 | 3 | ライセンス情報取得、利用状況取得、FL 利用状況エクスポート |
| 04\_ファイル関連 | 5 | アップロード、ダウンロード、情報更新、削除、情報エクスポート |
| 05\_シナリオ関連 | 4 | 登録、更新、削除、情報エクスポート |
| 06\_スケジュール関連 | 18 | 登録・更新（即時/日時指定/毎日/毎週/毎月/月末/条件指定）、有効化/無効化、削除、情報エクスポート |
| 07\_タスク関連 | 3 | 情報エクスポート、削除、アーカイブファイル登録履歴取得 |
| 08\_イベント関連 | 3 | ログ取得、ログ件数取得、情報エクスポート |
| 09\_ユーザ関連 | 6 | 登録、更新、削除、情報エクスポート、情報インポート、承認待ちスケジュール情報エクスポート |
| 10\_所属関連 | 5 | 登録、更新、削除、情報エクスポート、情報インポート |

---

## テスト実行

```powershell
poetry run pytest
```

---

## 開発環境

- Python 3.12.8（32bit 固定）
- Poetry による依存管理
- VSCode + flake8 / black / isort / pytest
- pre-commit によるコードチェック

---

## 開発ツール

### 依存パッケージのベンダリング

外部依存（requests, pycryptodome 等）を `_vendor/` に同梱します。

```powershell
poetry run vendor
```

### パッケージの配置

難読化済みパッケージを公開フォルダへコピーします。

```powershell
poetry run copy-to-public
```

### マニュアル自動生成

WinActor ノードのメタデータから MkDocs ドキュメントを生成します。

```powershell
poetry run generate-manual
poetry run generate-manual --build          # HTML ビルド + ZIP 作成
poetry run generate-manual --build --no-zip # HTML ビルドのみ
poetry run generate-manual --clean          # 生成済みファイルのクリーンアップ
```

### リリース

バージョン更新と ZIP パッケージの作成を行います。

```powershell
# パッチバージョンを更新して ZIP 作成
python tools/release.py --bump patch

# マイナーバージョンを更新して Git タグ付きで push
python tools/release.py --bump minor --tag
```

| オプション | 説明 |
|---|---|
| `--bump` | バージョン更新種別（必須）: `major` / `minor` / `patch` |
| `--tag` | `pyproject.toml` のバージョン更新 + commit + Git タグ `vX.Y.Z` の作成・push |

出力先: `dist/<リポジトリ名>-v<バージョン>.zip`
