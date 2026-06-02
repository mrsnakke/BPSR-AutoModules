[Setup]
; Este ID es único para tu programa, no lo cambies en futuras versiones
AppId={{B8F7A1C2-E23D-4B5A-9F8E-7D6C5B4A3F2E}
AppName=BPSR Module Optimizer
AppVersion=1.1
AppPublisher=MrSnake
DefaultDirName={autopf}\BPSR Module Optimizer
DefaultGroupName=BPSR Module Optimizer
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=BPSR Module Optimizer Setup v1.1
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SourceDir=.
UninstallDisplayIcon={app}\gui_app.exe
PrivilegesRequired=admin
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Reemplaza y añade todos los archivos necesarios
Source: "dist\gui_app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "Back.webp"; DestDir: "{app}"; Flags: ignoreversion
Source: "Font Awesome 7 Free-Solid-900.otf"; DestDir: "{app}"; Flags: ignoreversion
Source: "custom_presets.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "Fix Names.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "Icons\*"; DestDir: "{app}\Icons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Modulos\*"; DestDir: "{app}\Modulos"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Module-Effects\*"; DestDir: "{app}\Module-Effects"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "npcap-1.83.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{autoprograms}\BPSR Module Optimizer"; Filename: "{app}\gui_app.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\BPSR Module Optimizer"; Filename: "{app}\gui_app.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{tmp}\npcap-1.83.exe"; Parameters: ""; StatusMsg: "Instalando Npcap..."; Flags: waituntilterminated
Filename: "{app}\gui_app.exe"; Description: "{cm:LaunchProgram,BPSR Module Optimizer}"; Flags: nowait postinstall skipifsilent