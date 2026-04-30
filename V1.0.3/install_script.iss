[Setup]
AppName=Web端自动化测试工具
AppVersion=1.0.0
DefaultDirName={sd}\Web端自动化测试工具
DefaultGroupName=Web端自动化测试工具
OutputDir=.\installer_output
OutputBaseFilename=Web端自动化测试工具_安装包_v1.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\Web端自动化测试工具.exe

[Files]
Source: "dist\Web端自动化测试工具.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Web端自动化测试工具"; Filename: "{app}\Web端自动化测试工具.exe"
Name: "{userdesktop}\Web端自动化测试工具"; Filename: "{app}\Web端自动化测试工具.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "创建桌面快捷方式"; Flags: checkedonce

[Run]
Filename: "{app}\Web端自动化测试工具.exe"; Description: "运行工具"; Flags: nowait postinstall skipifsilent