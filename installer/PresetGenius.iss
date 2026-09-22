; PresetGenius installer. Build with installer\build.ps1
; Defines: Stage, Redist, Version

#ifndef Stage
  #error Set Stage to the staging directory
#endif
#ifndef Version
  #define Version "1.0.0"
#endif

[Setup]
AppId={{A7E3C1D4-5B28-4F0E-9C6A-8D2F1E0B7A44}
AppName=PresetGenius
AppVersion={#Version}
AppPublisher=PresetGenius
AppPublisherURL=https://github.com/PotATO-0-o/PresetGenius
DefaultDirName={autopf}\PresetGenius
DefaultGroupName=PresetGenius
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=PresetGenius-Setup-{#Version}
SetupLogging=yes
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
LicenseFile={#Stage}\licenses\GPL-3.0.txt
InfoAfterFile={#Stage}\README.txt
MinVersion=10.0

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "{cm:TypeFull}"
Name: "standalone"; Description: "{cm:TypeStandalone}"
Name: "vst3"; Description: "{cm:TypeVst3}"
Name: "custom"; Description: "{cm:TypeCustom}"; Flags: iscustom

[Components]
Name: "standalone"; Description: "{cm:CompStandalone}"; Types: full standalone custom; Flags: disablenouninstallwarning
Name: "vst3"; Description: "{cm:CompVst3}"; Types: full vst3 custom; Flags: disablenouninstallwarning

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Components: standalone
Name: "setupai"; Description: "{cm:TaskAi}"; GroupDescription: "{cm:TaskAiGroup}"; Flags: checkedonce

[Files]
Source: "{#Stage}\PresetGenius.exe"; DestDir: "{app}"; Components: standalone; Flags: ignoreversion
Source: "{#Stage}\PresetGenius.vst3"; DestDir: "{commoncf64}\VST3"; Components: vst3; Flags: ignoreversion uninsrestartdelete
Source: "{#Stage}\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Stage}\requirements-ai.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Stage}\Setup-AI.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Stage}\Start-PresetGenius.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Stage}\Start-Server.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#Stage}\server\*"; DestDir: "{app}\server"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Stage}\ml\*"; DestDir: "{app}\ml"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#Stage}\licenses\*"; DestDir: "{app}\licenses"; Flags: ignoreversion
Source: "{#Redist}\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "{#Stage}\redist\python-3.11.9-amd64.exe"; DestDir: "{app}\redist"; Flags: ignoreversion

[Icons]
Name: "{group}\PresetGenius"; Filename: "{app}\Start-PresetGenius.cmd"; WorkingDir: "{app}"; Comment: "{cm:ShortcutStandalone}"; Components: standalone; IconFilename: "{app}\PresetGenius.exe"
Name: "{group}\PresetGenius AI Server"; Filename: "{app}\Start-Server.cmd"; WorkingDir: "{app}"; Comment: "{cm:ShortcutServer}"
Name: "{group}\Setup AI"; Filename: "{app}\Setup-AI.cmd"; WorkingDir: "{app}"
Name: "{autodesktop}\PresetGenius"; Filename: "{app}\Start-PresetGenius.cmd"; WorkingDir: "{app}"; Components: standalone; Tasks: desktopicon; IconFilename: "{app}\PresetGenius.exe"

[Run]
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "{cm:VcRedist}"; Flags: waituntilterminated
Filename: "{app}\Setup-AI.cmd"; Description: "{cm:RunSetupAi}"; Tasks: setupai; Flags: postinstall waituntilterminated
Filename: "{app}\Start-PresetGenius.cmd"; Description: "{cm:RunApp}"; Components: standalone; Flags: postinstall nowait skipifsilent
Filename: "{app}\Start-Server.cmd"; Description: "{cm:RunServer}"; Components: vst3; Flags: postinstall nowait skipifsilent unchecked

[Code]
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectComponents then
  begin
    if (not WizardIsComponentSelected('standalone')) and (not WizardIsComponentSelected('vst3')) then
    begin
      MsgBox(CustomMessage('NeedOneComponent'), mbError, MB_OK);
      Result := False;
    end;
  end;
end;

[CustomMessages]
TypeFull=Standalone и VST3
TypeStandalone=Только Standalone
TypeVst3=Только VST3
TypeCustom=Выборочная установка
CompStandalone=Standalone — отдельная программа
CompVst3=VST3 — плагин для Ableton и других DAW
TaskAi=Скачать библиотеки ИИ после установки (интернет, около 2 ГБ)
TaskAiGroup=Искусственный интеллект
ShortcutStandalone=Запустить синтезатор и сервер ИИ
ShortcutServer=Только сервер ИИ для плагина VST3
VcRedist=Установка Visual C++...
RunSetupAi=Скачать библиотеки ИИ сейчас
RunApp=Запустить PresetGenius
RunServer=Запустить сервер ИИ
NeedOneComponent=Выберите Standalone, VST3 или оба варианта.
english.TypeFull=Standalone and VST3
english.TypeStandalone=Standalone only
english.TypeVst3=VST3 only
english.TypeCustom=Custom installation
english.CompStandalone=Standalone application
english.CompVst3=VST3 plugin for Ableton and other DAWs
english.TaskAi=Download AI libraries after setup (internet, about 2 GB)
english.TaskAiGroup=Artificial intelligence
english.ShortcutStandalone=Start the synth and the AI server
english.ShortcutServer=AI server for the VST3 plugin
english.VcRedist=Installing Visual C++...
english.RunSetupAi=Download AI libraries now
english.RunApp=Launch PresetGenius
english.RunServer=Start the AI server
english.NeedOneComponent=Select Standalone, VST3, or both.
