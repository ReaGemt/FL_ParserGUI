[Setup]
AppName=FL Parser GUI
AppVersion=1.0
DefaultDirName={pf}\FL_Parser_GUI
DefaultGroupName=FL Parser GUI
OutputDir=dist
OutputBaseFilename=FL_Parser_GUI_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\FL_ParserGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "gui_decorations.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "rss_parser.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "RSS_INSTRUCTIONS.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "tasks.xlsx"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "dist\.env"; DestDir: "{app}"; Flags: onlyifdoesntexist
Source: "dist\app.log"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\FL Parser GUI"; Filename: "{app}\FL_ParserGUI.exe"
Name: "{group}\Uninstall FL Parser GUI"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\FL_ParserGUI.exe"; Description: "Запустить FL Parser GUI"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\.env"
Type: files; Name: "{app}\app.log"
Type: files; Name: "{app}\tasks.xlsx"
