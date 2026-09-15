; ─────────────────────────────────────────────────────────────────────
;  Extractor de Recibos a Excel v1.0.3 - Instalador NSIS
; ─────────────────────────────────────────────────────────────────────
!include "MUI2.nsh"
!include "LogicLib.nsh"

; ── Metadata ────────────────────────────────────────────────────────────────
!define PAYLOAD "C:\Users\elias\AppData\Local\Temp\installer_payload"
!define SRC_ROOT "C:\Users\elias\OneDrive\Desktop\PROYECTO DE EXTRACTOR DE PDF"

Name "Extractor de Recibos a Excel"
OutFile "${PAYLOAD}\ExtractorRecibos_Setup_v1.0.5.exe"
InstallDir "$PROGRAMFILES\Extractor de Recibos"
InstallDirRegKey HKLM "Software\Extractor de Recibos" "InstallDir"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show
BrandingText "Extractor de Recibos a Excel v1.0.5"

; ── Version info ───────────────────────────────────────────────────────────
VIProductVersion "1.0.5.0"
VIAddVersionKey "ProductName" "Extractor de Recibos a Excel"
VIAddVersionKey "ProductVersion" "1.0.5.0"
VIAddVersionKey "FileDescription" "Instalador de Extractor de Recibos a Excel"
VIAddVersionKey "LegalCopyright" "2026"
VIAddVersionKey "FileVersion" "1.0.5.0"
VIAddVersionKey "CompanyName" "Extractor de Recibos"

; ── Interface ──────────────────────────────────────────────────────────────
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\nsis.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\win.bmp"
!define MUI_ABORTWARNING
!define MUI_ICON "${SRC_ROOT}\assets\icon.ico"
!define MUI_UNICON "${SRC_ROOT}\assets\icon.ico"

; ── Pages ──────────────────────────────────────────────────────────────────
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${SRC_ROOT}\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\ExtractorRecibos.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Abrir Extractor de Recibos"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; ── Languages ──────────────────────────────────────────────────────────────
!insertmacro MUI_LANGUAGE "SpanishInternational"

; ── Install section ────────────────────────────────────────────────────────
Section "Instalar Extractor de Recibos" SecMain
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Copiar todos los archivos de la aplicacion (PyInstaller --onedir)
    File /r "${PAYLOAD}\_internal"
    File "${PAYLOAD}\ExtractorRecibos.exe"

    ; Crear acceso directo en Menú Inicio
    CreateDirectory "$SMPROGRAMS\Extractor de Recibos"
    CreateShortcut "$SMPROGRAMS\Extractor de Recibos\Extractor de Recibos.lnk" "$INSTDIR\ExtractorRecibos.exe" "" "$INSTDIR\ExtractorRecibos.exe" 0
    CreateShortcut "$SMPROGRAMS\Extractor de Recibos\Desinstalar.lnk" "$INSTDIR\Uninstall.exe"

    ; Acceso directo en escritorio
    CreateShortcut "$DESKTOP\Extractor de Recibos.lnk" "$INSTDIR\ExtractorRecibos.exe" "" "$INSTDIR\ExtractorRecibos.exe" 0

    ; Registry keys para Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "DisplayName" "Extractor de Recibos a Excel"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "DisplayIcon" "$\"$INSTDIR\ExtractorRecibos.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "Publisher" "Extractor de Recibos"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "DisplayVersion" "1.0.5.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" "NoRepair" 1

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Guardar ruta de instalación
    WriteRegStr HKLM "Software\Extractor de Recibos" "InstallDir" "$INSTDIR"
SectionEnd

; ── Uninstaller ────────────────────────────────────────────────────────────
Section "Uninstall"
    RMDir /r "$INSTDIR"
    RMDir /r "$SMPROGRAMS\Extractor de Recibos"
    Delete "$DESKTOP\Extractor de Recibos.lnk"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos"
    DeleteRegKey HKLM "Software\Extractor de Recibos"

    ; Limpiar mapeos y configs (opcional)
    ; RMDir /r "$LOCALAPPDATA\ExtractorRecibos"
SectionEnd
