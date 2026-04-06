# 導入ガイド

WinActor for WMC を利用するには、ライセンス認証、WinActor for WMC のインストール、および WinActor の設定が必要です。

はじめに、提供された ZIP ファイル（例: WinActor WMC連携MSYSライブラリ一式_V100.zip）を任意の場所に解凍してください。

!!! info "バージョン番号について"
    ZIP ファイル名末尾の `V100` はバージョンにより異なります（例: V100 = v1.0.0、V110 = v1.1.0）。

解凍後のフォルダ構成は以下のとおりです。

```
WinActor WMC連携MSYSライブラリ一式_V***/
├── winactor-for-wmc-setup-v*.*.*.exe  … インストーラ
├── MSYS_WMC連携_v*.*.*/               … ライブラリ本体
│   ├── 01_認証関連/
│   ├── 02_WinActor関連/
│   │   ...
│   └── 10_所属関連/
├── マニュアル/                         … 本マニュアル
└── ライセンス認証ツール/               … ライセンス認証ツール
    └── winactor-adapters-license-authenticator.exe
```

## 1. ライセンス認証

解凍したフォルダ内の `ライセンス認証ツール` フォルダに含まれる認証ツールを使用して、ライセンスの登録を行います。

!!! warning "重要"
    ライセンス認証が完了していないと WinActor for WMC ライブラリを使用することが出来ません。

:material-arrow-right: [ライセンス認証](license.md)

## 2. WinActor for WMC のインストール

解凍したフォルダ内の `winactor-for-wmc-setup-v{バージョン番号}.exe` を実行し、関連ファイルをインストールします。

:material-arrow-right: [WinActor for WMC のインストール](install.md)

## 3. WinActor の設定

WinActor にライブラリを追加し、WMC への接続情報を設定します。

:material-arrow-right: [WinActor の設定](winactor.md)
