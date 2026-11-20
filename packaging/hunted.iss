; Inno Setup script for the Windows installer (hunted-windows-setup.exe).
;
; Build (after `pyinstaller hunted.spec --noconfirm` made dist\hunted):
;   iscc /DAppVersion=0.3.0 packaging\hunted.iss
; The release workflow does this and passes the version from the tag (pyproject.toml on a
; manual run).
;
; Reusable for other pygamine games: change AppId (generate a new GUID once, never change it
; afterwards), MyAppName, MyExeName, the output name and the [Languages] list.

#ifndef AppVersion
  #define AppVersion "0.0.0-dev"
#endif
#define MyAppName "The Hunted"
#define MyExeName "hunted.exe"

[Setup]
; Fixed for this game forever: it is how Windows (and a newer installer) recognizes the install.
AppId={{75294B26-A7AF-4438-A800-361A1B30F491}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher=VectorViolet
; Installs for all users into Program Files by default (the setup asks for admin rights); its
; dialog also offers "only for me", which installs per-user ({autopf} then maps to the user's
; Programs folder).
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={autopf}\hunted
; Always show the folder page, so players can pick e.g. C:\Games.
DisableDirPage=no
DisableProgramGroupPage=yes
; Language dialog at the start; the choice only sets the language of the setup itself.
ShowLanguageDialog=yes
UsePreviousLanguage=no
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyExeName}
OutputDir=..\installer-out
OutputBaseFilename=hunted-windows-setup
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; An update must not leave files the new build no longer ships (old DLLs would sit beside the
; new ones). The game keeps no saves, so nothing of the player's is in the folder.
; Only where our own exe already is, so a folder the player picked that holds something else
; (say C:\Games with another game's _internal) is never wiped.
Type: filesandordirs; Name: "{app}\_internal"; Check: IsOurInstall

[Files]
; The whole PyInstaller onedir output, including _internal.
Source: "..\dist\hunted\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

; The uninstaller removes only what the installer put in the install folder (and the shortcuts).

[Code]
// True when the chosen folder already holds a Hunted install (an update or a reinstall).
function IsOurInstall: Boolean;
begin
  Result := FileExists(ExpandConstant('{app}\{#MyExeName}'));
end;
