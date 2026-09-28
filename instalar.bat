@echo off
REM ============================================================
REM  Extractor de Recibos a Excel v1.0.6
REM  Instalador y lanzador portable - SIN .EXE
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
echo ============================================================
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
echo.
echo    Voy a abrir la pagina de descarga en tu navegador.
echo    Cuando se abra la pagina:
echo      1. Click en el boton amarillo "Download Python 3.x.x"
echo      2. Ejecuta el instalador descargado
echo      3. MUY IMPORTANTE: tilda "Add Python to PATH" al inicio
echo      4. Click "Install Now"
echo      5. Espera a que termine y volve a ejecutar este instalador
echo.
start https://www.python.org/downloads/
echo.
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
    echo.
    echo    ERROR: Tkinter no disponible.
    echo.
    echo    Esto pasa cuando Python se instala sin soporte grafico.
    echo    Solucion: reinstala Python y asegurate de marcar
    echo    "tcl/tk and IDLE" en la instalacion personalizada.
    echo.
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

REM ── Paso 4: Verificar Tesseract (opcional) ─────────────────────
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
        echo.
        echo    Si queres OCR, descarga Tesseract desde:
        echo    https://github.com/UB-Mannheim/tesseract/releases
        echo    (la version "tesseract-ocr-w64-setup-5.x.x.exe")
    )
) else (
    echo    Tesseract OK
)

REM ── Paso 5: Crear accesos directos ────────────────────────────
echo.
echo [5/6] Creando accesos directos...

set "INSTALL_DIR=%LOCALAPPDATA%\ExtractorRecibos"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copiar todos los archivos a la carpeta de instalacion
xcopy /E /I /Y "src" "%INSTALL_DIR%\src" >nul 2>&1
copy /Y "main.py" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "requirements.txt" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "assets" "%INSTALL_DIR%\assets" >nul 2>&1

REM Crear el .bat lanzador en la carpeta de instalacion
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo %PY% main.py
    echo if errorlevel 1 pause
) > "%INSTALL_DIR%\ExtractorRecibos.bat"

REM Acceso directo en escritorio
set "DESKTOP=%USERPROFILE%\Desktop"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Escritorio"
if not exist "%DESKTOP%" set "DESKTOP=%PUBLIC%\Desktop"

if not exist "%START_MENU%\Extractor de Recibos" mkdir "%START_MENU%\Extractor de Recibos"

REM Crear acceso directo (.lnk) usando PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\Extractor de Recibos.lnk'); $s.TargetPath = '%INSTALL_DIR%\ExtractorRecibos.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = '%INSTALL_DIR%\assets\icon.ico'; $s.Description = 'Extractor de Recibos a Excel'; $s.Save()" 2>nul

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%START_MENU%\Extractor de Recibos\Extractor de Recibos.lnk'); $s.TargetPath = '%INSTALL_DIR%\ExtractorRecibos.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.IconLocation = '%INSTALL_DIR%\assets\icon.ico'; $s.Description = 'Extractor de Recibos a Excel'; $s.Save()" 2>nul

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%START_MENU%\Extractor de Recibos\Desinstalar.lnk'); $s.TargetPath = '%INSTALL_DIR%\desinstalar.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Desinstalar Extractor de Recibos'; $s.Save()" 2>nul

REM Registro para Add or Remove Programs
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "DisplayName" /t REG_SZ /d "Extractor de Recibos a Excel" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "DisplayVersion" /t REG_SZ /d "1.0.6" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "Publisher" /t REG_SZ /d "Extractor de Recibos" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "UninstallString" /t REG_SZ /d "\"%INSTALL_DIR%\desinstalar.bat\"" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\assets\icon.ico" /f >nul 2>&1

REM Crear script de desinstalacion
(
    echo @echo off
    echo echo Desinstalando Extractor de Recibos...
    echo reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Extractor de Recibos" /f ^>nul 2^>^&1
    echo del /Q "%DESKTOP%\Extractor de Recibos.lnk" 2^>nul
    echo del /Q "%START_MENU%\Extractor de Recibos\Extractor de Recibos.lnk" 2^>nul
    echo del /Q "%START_MENU%\Extractor de Recibos\Desinstalar.lnk" 2^>nul
    echo rmdir /S /Q "%START_MENU%\Extractor de Recibos" 2^>nul
    echo rmdir /S /Q "%INSTALL_DIR%" 2^>nul
    echo echo Desinstalacion completa.
    echo pause
) > "%INSTALL_DIR%\desinstalar.bat"

echo    Accesos directos creados:
echo      - Escritorio: "Extractor de Recibos"
echo      - Menu Inicio: "Extractor de Recibos"
echo      - Desinstalar: en Configuracion - Aplicaciones

REM ── Paso 6: Abrir la aplicacion ─────────────────────────────────
echo.
echo [6/6] Todo listo!
echo.
echo ============================================================
echo   Instalacion completa!
echo.
echo   La aplicacion se abrira en unos segundos.
echo.
echo   Para abrirla en el futuro:
echo     - Doble clic en el acceso directo del escritorio
echo     - O buscala en el Menu Inicio
echo.
echo   Para desinstalar:
echo     - Configuracion - Aplicaciones - Extractor de Recibos
echo ============================================================
echo.
pause

REM Marcar como instalado
%PY% -c "import sys; sys.path.insert(0, '.'); from src.core import mappings as m; s = m.load_settings(); s['tesseract_installed'] = True; s['first_run'] = False; m.save_settings(s)" 2>nul

REM Abrir la aplicacion
cd /d "%INSTALL_DIR%"
%PY% main.py

endlocal
