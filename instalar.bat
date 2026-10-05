@echo off
REM ============================================================
REM  Extractor de Recibos a Excel v1.0.6
REM  Instalador completo (sin .exe)
REM ============================================================

chcp 65001 > nul
title Extractor de Recibos - Instalador
setlocal enabledelayedexpansion

cd /d "%~dp0"

cls
echo.
echo ============================================================
echo    INSTALADOR - Extractor de Recibos a Excel v1.0.6
echo ============================================================
echo.
echo  Este programa instala todo lo necesario y crea accesos
echo  directos para usar el Extractor de Recibos.
echo.
echo  NO genera archivos .exe (evita los avisos de Windows).
echo.
pause
cls

REM ── Paso 1: Verificar / instalar Python ───────────────────────
echo.
echo [1/6] Verificando Python...
where py >nul 2>nul
if not errorlevel 1 (set "PY=py" & goto :py_ok)
where python >nul 2>nul
if not errorlevel 1 (set "PY=python" & goto :py_ok)

echo.
echo    Python NO esta instalado en tu sistema.
echo.
echo    NECESITAS Python 3.11 o superior.
echo    Se abrira la pagina de descarga. Durante la instalacion
echo    tilda "Add Python to PATH".
echo.
start https://www.python.org/downloads/
pause
exit /b 1

:py_ok
for /f "tokens=2" %%i in ('%PY% --version 2^>^&1') do set "PYVER=%%i"
echo    Python !PYVER! OK

REM ── Paso 2: Verificar Tkinter ──────────────────────────────────
echo.
echo [2/6] Verificando Tkinter...
%PY% -c "import tkinter" 2>nul
if errorlevel 1 (
    echo    ERROR: Tkinter no disponible. Reinstala Python con tcl/tk.
    pause
    exit /b 1
)
echo    Tkinter OK

REM ── Paso 3: Instalar dependencias ──────────────────────────────
echo.
echo [3/6] Instalando dependencias (solo la primera vez)...
%PY% -m pip install --upgrade pip --quiet --disable-pip-version-check
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo    ERROR instalando dependencias.
    pause
    exit /b 1
)
echo    Dependencias instaladas

REM ── Paso 4: Verificar Tesseract ─────────────────────────────────
echo.
echo [4/6] Verificando Tesseract OCR...
where tesseract >nul 2>nul
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\ExtractorRecibos\tesseract\tesseract.exe" (
        set "PATH=%PATH%;%LOCALAPPDATA%\ExtractorRecibos\tesseract"
        echo    Tesseract encontrado en AppData
    ) else (
        echo    Tesseract no encontrado.
        echo    Solo podras procesar PDFs con texto digital.
        echo    Para OCR: descarga Tesseract desde
        echo    https://github.com/UB-Mannheim/tesseract/releases
    )
) else (
    echo    Tesseract OK
)

REM ── Paso 5: Instalar y crear accesos directos ──────────────────
echo.
echo [5/6] Instalando y creando accesos directos...

set "INSTALL_DIR=%LOCALAPPDATA%\ExtractorRecibos"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copiar archivos a la carpeta de instalacion
xcopy /E /I /Y "src" "%INSTALL_DIR%\src" >nul 2>&1
copy /Y "main.py" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "requirements.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y "assets" "%INSTALL_DIR%\assets" >nul 2>&1

REM Crear el .bat lanzador
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo %PY% main.py
    echo if errorlevel 1 pause
) > "%INSTALL_DIR%\ExtractorRecibos.bat"

REM Crear desinstalador
(
    echo @echo off
    echo reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /f ^>nul 2^>^&1
    echo del /Q "%DESKTOP_DIR%\Extractor de Recibos.lnk" 2^>nul
    echo del /Q "%START_MENU%\Extractor de Recibos\Extractor de Recibos.lnk" 2^>nul
    echo rmdir /S /Q "%INSTALL_DIR%" 2^>nul
    echo echo Desinstalacion completa.
    echo pause
) > "%INSTALL_DIR%\desinstalar.bat"

REM Detectar escritorio desde el registro (soporta OneDrive redirection)
set "DESKTOP_DIR="
for /f "delims=" %%P in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop 2^>nul ^| findstr /i "REG_"') do set "RAW=%%P"
for /f "tokens=2*" %%A in ("!RAW!") do set "RAW=%%B"
call set "DESKTOP_DIR=%%RAW:%USERPROFILE\=%USERPROFILE%%%"
if not exist "!DESKTOP_DIR!" set "DESKTOP_DIR=!RAW!"
if not exist "!DESKTOP_DIR!" (
    if exist "%USERPROFILE%\Desktop" set "DESKTOP_DIR=%USERPROFILE%\Desktop"
    if exist "%USERPROFILE%\Escritorio" set "DESKTOP_DIR=%USERPROFILE%\Escritorio"
)
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU%\Extractor de Recibos" mkdir "%START_MENU%\Extractor de Recibos"

REM Crear accesos directos con VBScript
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
    echo Set s3 = WshShell.CreateShortcut("%START_MENU%\Extractor de Recibos\Desinstalar.lnk"^)
    echo s3.TargetPath = "%INSTALL_DIR%\desinstalar.bat"
    echo s3.WorkingDirectory = "%INSTALL_DIR%"
    echo s3.Description = "Desinstalar Extractor de Recibos"
    echo s3.Save
    echo WScript.Echo "OK Desinstalador"
) > "%VBS%"
cscript //NoLogo "%VBS%" >nul 2>&1
del "%VBS%" 2>nul

REM Registro en Add or Remove Programs
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "DisplayName" /t REG_SZ /d "Extractor de Recibos a Excel" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "DisplayVersion" /t REG_SZ /d "1.0.6" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "Publisher" /t REG_SZ /d "Extractor de Recibos" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "UninstallString" /t REG_SZ /d "\"%INSTALL_DIR%\desinstalar.bat\"" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\assets\icon.ico" /f >nul 2>&1

REM ── Paso 6: Marcar y abrir ──────────────────────────────────────
echo.
echo [6/6] Todo listo!
echo.
echo ============================================================
echo   Instalacion completa!
echo.
echo   Accesos directos creados:
echo     - Escritorio: "Extractor de Recibos"
echo     - Menu Inicio: "Extractor de Recibos"
echo     - Desinstalar: "Desinstalar" en Menu Inicio
echo.
echo   La aplicacion se abrira en unos segundos.
echo ============================================================
echo.
pause

%PY% -c "import sys; sys.path.insert(0, '.'); from src.core import mappings as m; s = m.load_settings(); s['tesseract_installed'] = True; s['first_run'] = False; m.save_settings(s)" 2>nul

cd /d "%INSTALL_DIR%"
%PY% main.py

endlocal