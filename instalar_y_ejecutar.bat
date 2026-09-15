@echo off
chcp 65001 > nul
title Extractor de Recibos a Excel v1.0.5 - Instalador portable

setlocal

echo.
echo ============================================================
echo   Extractor de Recibos a Excel - Instalador Portable v1.0.5
echo ============================================================
echo.
echo   Este script instala todo desde el codigo fuente.
echo   NO genera ningun .exe, evita el aviso de Windows SmartScreen.
echo.
echo   Requisitos: Python 3.11 o superior
echo.
pause

REM ── Verificar Python ─────────────────────────────────────
where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo.
        echo [ERROR] Python no esta instalado.
        echo Descargalo desde: https://www.python.org/downloads/
        echo Marcá "Add Python to PATH" durante la instalacion.
        pause
        exit /b 1
    )
    set "PY=python"
) else (
    set "PY=py"
)

echo.
echo [1/5] Verificando version de Python...
%PY% --version

echo.
echo [2/5] Instalando dependencias Python (esto puede tardar unos minutos)...
%PY% -m pip install --upgrade pip --quiet
%PY% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    echo Verificá tu conexion a internet.
    pause
    exit /b 1
)
echo   OK dependencias instaladas.

echo.
echo [3/5] Verificando Tesseract OCR (para PDFs escaneados e imagenes)...
where tesseract >nul 2>nul
if errorlevel 1 (
    echo   Tesseract no encontrado, intentando descarga portable...
    %PY% -c "import urllib.request, os, zipfile; print('   OK script listo')" 2>nul
    echo.
    echo   Para OCR de PDFs escaneados, descarga Tesseract desde:
    echo   https://github.com/UB-Mannheim/tesseract/releases
    echo   Marcá los idiomas: Spanish, English, Portuguese
    echo.
    echo   Solo PDFs con texto (digitales) funcionaran sin Tesseract.
    echo.
) else (
    tesseract --version
    echo   Tesseract OK
)

echo.
echo [4/5] Marcando como instalado (para evitar wizard de primera vez)...
%PY% -c "import sys, os; sys.path.insert(0, '.'); from src.core import mappings as m; s = m.load_settings(); s['tesseract_installed'] = True; s['first_run'] = False; m.save_settings(s); print('   OK')"

echo.
echo [5/5] Iniciando Extractor de Recibos...
echo.
%PY% main.py

endlocal
