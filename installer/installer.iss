; InnoSetup script for winactor-for-wmc installer
; Installs pyarmor_runtime_011041 and winactor_for_wmc to a fixed path

#define MyAppName "WinActor for WMC"
#define MyAppPublisher "MSYS"

; Version is passed via /D command-line option at compile time
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

[Setup]
AppId={{E8A3F2B1-7C4D-4E5F-9A1B-3D6E8F0C2A7B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName=C:\Users\Public\msys-winactor-adapters\libs
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputBaseFilename=winactor-for-wmc-setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
CreateAppDir=yes
Uninstallable=yes
UninstallDisplayName={#MyAppName}

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
; pyarmor_runtime_011041 - always overwrite without warning
Source: "{#SourceDir}\pyarmor_runtime_011041\*"; DestDir: "{app}\pyarmor_runtime_011041"; Flags: ignoreversion recursesubdirs createallsubdirs

; winactor_for_wmc - obfuscated package with vendored dependencies
Source: "{#SourceDir}\winactor_for_wmc\*"; DestDir: "{app}\winactor_for_wmc"; Flags: ignoreversion recursesubdirs createallsubdirs
