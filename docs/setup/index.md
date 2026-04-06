# 導入ガイド

WinActor for WMC を利用するには、ライセンス認証、WinActor for WMC のインストール、および WinActor の設定が必要です。

はじめに、提供された ZIP ファイル（WinActor WMC連携MSYSライブラリ一式_V{バージョン番号}.zip）を任意の場所に解凍してください。

解凍後のフォルダ構成は以下のとおりです。

```
WinActor WMC連携MSYSライブラリ一式_V{バージョン番号}/
├── winactor-for-wmc-setup-v{バージョン番号}.exe  … インストーラ
├── MSYS_WMC連携_v{バージョン番号}/               … ライブラリ本体
│   ├── 01_認証関連/
│   ├── 02_WinActor関連/
│   │   ...
│   └── 10_所属関連/
└── マニュアル/                                    … 本マニュアル
```

## 1. ライセンス認証

MSYS WinActor Adapters ライセンス認証ツールを使用して、ライセンスの登録を行います。

!!! warning "重要"
    ライセンス認証が完了していないと WinActor for WMC ライブラリを使用することが出来ません。

:material-arrow-right: [ライセンス認証](license.md)

## 2. WinActor for WMC のインストール

解凍したフォルダ内の `winactor-for-wmc-setup-v{バージョン番号}.exe` を実行し、関連ファイルをインストールします。

:material-arrow-right: [WinActor for WMC のインストール](install.md)

## 3. WinActor の設定

WinActor にライブラリを追加し、WMC への接続情報を設定します。

:material-arrow-right: [WinActor の設定](winactor.md)
