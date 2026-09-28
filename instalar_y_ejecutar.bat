@echo off
REM ─────────────────────────────────────────────────────────────────
REM  Extractor de Recibos a Excel v1.0.6
REM  Lanzador portable - NO requiere instalacion de .exe
REM ─────────────────────────────────────────────────────────────────

chcp 65001 > nul
title Extractor de Recibos a Excel v1.0.6
setlocal enabledelayedexpansion

REM Cambiar al directorio del script
cd /d "%~dp0"

echo.
echo ============================================================
echo   Extractor de Recibos a Excel v1.0.6
echo ============================================================
echo.

REM ── Paso 1: Verificar Python ─────────────────────────────────
echo [1/5] Verificando Python...

where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py"
    set "PY_OK=1"
    goto :python_ok
)

where python >nul 2>nul
if not errorlevel 1 (
    set "PY=python"
    set "PY_OK=1"
    goto :python_ok
)

echo.
echo [ERROR] Python no esta instalado.
echo.
echo Necesitas instalar Python 3.11 o superior.
echo Descargalo desde: https://www.python.org/downloads/
echo IMPORTANTE: durante la instalacion, tilda "Add Python to PATH"
echo.
echo Si ya lo instalaste, abrila con "Agregar al PATH" marcada.
echo.
pause
exit /b 1

:python_ok
for /f "tokens=2" %%i in ('%PY% --version 2^>^&1') do set "PYVER=%%i"
echo   OK: Python !PYVER!

REM ── Paso 2: Verificar Tkinter ───────────────────────────────
echo.
echo [2/5] Verificando Tkinter (necesario para la interfaz grafica)...
%PY% -c "import tkinter" 2>nul
if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] Tkinter no esta disponible.
    echo Esto pasa con instalaciones de Python minimas (sin tcl/tk).
    echo.
    echo Solucion 1 - Reinstalar Python:
    echo   1. Desinstala Python actual
    echo   2. Descarga Python desde python.org/downloads
    echo   3. En la instalacion, "Install launcher for all users"
    echo      y elegi "Customize installation"
    echo   4. Asegarate que "tcl/tk and IDLE" este marcado
    echo.
    echo Solucion 2 - Continuar igual (puede fallar al abrir la GUI):
    echo.
    set /p "CONTINUE=Queres continuar igual? (s/n): "
    if /i not "!CONTINUE!"=="s" exit /b 1
) else (
    echo   OK
)

REM ── Paso 3: Instalar dependencias ────────────────────────────
echo.
echo [3/5] Instalando dependencias (solo la primera vez)...
%PY% -m pip install --upgrade pip --quiet --disable-pip-version-check 2>nul
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la instalacion de dependencias.
    echo Verifica tu conexion a internet.
    pause
    exit /b 1
)
echo   OK dependencias instaladas.

REM ── Paso 4: Verificar Tesseract ──────────────────────────────
echo.
echo [4/5] Verificando Tesseract OCR...
where tesseract >nul 2>nul
if errorlevel 1 (
    if exist "C:\Users\%USERNAME%\AppData\Local\ExtractorRecibos\tesseract\tesseract.exe" (
        set "PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\ExtractorRecibos\tesseract"
        echo   Tesseract encontrado en AppData
    ) else (
        echo   Tesseract no encontrado.
        echo   Solo podras procesar PDFs con texto digital.
        echo   Para OCR de PDFs escaneados, descarga Tesseract desde:
        echo   https://github.com/UB-Mannheim/tesseract/releases
    )
) else (
    echo   OK
)

REM ── Paso 5: Marcar como instalado y abrir la app ────────────
echo.
echo [5/5] Iniciando aplicacion...
echo.

%PY% -c "import sys; sys.path.insert(0, '.'); from src.core import mappings as m; s = m.load_settings(); s['tesseract_installed'] = True; s['first_run'] = False; m.save_settings(s)" 2>nul

%PY% main.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   La aplicacion finalizo con error.
    echo ============================================================
    echo.
    pause
)

endlocal
