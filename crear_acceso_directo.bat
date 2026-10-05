@echo off
chcp 65001 > nul
title Extractor de Recibos - Acceso Directo
setlocal enabledelayedexpansion
cd /d "%~dp0"
cls
echo.
echo ============================================================
echo   Extractor de Recibos - Acceso Directo
echo ============================================================
echo.
pause
set "INSTALL_DIR=%LOCALAPPDATA%\ExtractorRecibos"
if not exist "%INSTALL_DIR%\main.py" (
    set /p "INSTALL_DIR=Carpeta de la app: "
    if not exist "!INSTALL_DIR!\main.py" (
        echo ERROR: No se encontro main.py
        pause
        exit /b 1
    )
)
REM Detectar escritorio (lee del registro y expande variables)
set "DESKTOP_DIR="
for /f "delims=" %%P in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop /reg:64 2^>nul ^| findstr /i "REG_"') do (
    set "RAW=%%P"
)
if not defined RAW (
    for /f "delims=" %%P in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop 2^>nul ^| findstr /i "REG_"') do (
        set "RAW=%%P"
    )
)
REM Tomar solo el path (despues del tipo REG_)
for /f "tokens=2*" %%A in ("!RAW!") do set "RAW=%%B"
call set "DESKTOP_DIR=%%RAW:%USERPROFILE\=%USERPROFILE%%%"
if not exist "!DESKTOP_DIR!" set "DESKTOP_DIR=!RAW!"
if not exist "!DESKTOP_DIR!" (
    if exist "%USERPROFILE%\Desktop" set "DESKTOP_DIR=%USERPROFILE%\Desktop"
    if exist "%USERPROFILE%\Escritorio" set "DESKTOP_DIR=%USERPROFILE%\Escritorio"
)
if "!DESKTOP_DIR!"=="" (
    echo ERROR: No se encontro Escritorio
    pause
    exit /b 1
)
echo Instalacion: %INSTALL_DIR%
echo Escritorio: !DESKTOP_DIR!
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU%\Extractor de Recibos" mkdir "%START_MENU%\Extractor de Recibos"
set "VBS=%TEMP%\crear_acceso_%RANDOM%.vbs"
(
    echo Set WshShell = WScript.CreateObject("WScript.Shell"^)
    echo Set s = WshShell.CreateShortcut("!DESKTOP_DIR!\Extractor de Recibos.lnk"^)
    echo s.TargetPath = "%INSTALL_DIR%\ExtractorRecibos.bat"
    echo s.WorkingDirectory = "%INSTALL_DIR%"
    echo s.IconLocation = "%INSTALL_DIR%\assets\icon.ico"
    echo s.Description = "Extractor de Recibos a Excel"
    echo s.Save
    echo WScript.Echo "OK Escritorio"
    echo Set s2 = WshShell.CreateShortcut("%START_MENU%\Extractor de Recibos\Extractor de Recibos.lnk"^)
    echo s2.TargetPath = "%INSTALL_DIR%\ExtractorRecibos.bat"
    echo s2.WorkingDirectory = "%INSTALL_DIR%"
    echo s2.IconLocation = "%INSTALL_DIR%\assets\icon.ico"
    echo s2.Description = "Extractor de Recibos a Excel"
    echo s2.Save
    echo WScript.Echo "OK Menu Inicio"
) > "%VBS%"
cscript //NoLogo "%VBS%"
set "VBS_EXIT=%errorlevel%"
del "%VBS%" 2>nul
echo.
echo ============================================================
echo   Resultado:
echo ============================================================
if exist "!DESKTOP_DIR!\Extractor de Recibos.lnk" (
    echo   OK   Escritorio: !DESKTOP_DIR!\Extractor de Recibos.lnk
) else (
    echo   FALLO Escritorio
)
if exist "%START_MENU%\Extractor de Recibos\Extractor de Recibos.lnk" (
    echo   OK   Menu Inicio
) else (
    echo   FALLO Menu Inicio
)
echo.
pause
endlocal