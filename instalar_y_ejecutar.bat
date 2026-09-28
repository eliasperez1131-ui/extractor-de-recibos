@echo off
chcp 65001 > nul
title Extractor de Recibos v1.0.6
cd /d "%~dp0"
echo.
echo ============================================================
echo   Extractor de Recibos a Excel v1.0.6
echo ============================================================
echo.
REM Paso 1: Python
where py >nul 2>nul
if not errorlevel 1 (set "PY=py" & goto pyok)
where python >nul 2>nul
if not errorlevel 1 (set "PY=python" & goto pyok)
echo ERROR: Python no esta instalado. Descargalo desde https://www.python.org/downloads/
pause
exit /b 1
:pyok
echo OK Python encontrado
REM Paso 2: Tkinter
%PY% -c "import tkinter" 2>nul
if errorlevel 1 (echo ERROR: Tkinter no disponible & pause & exit /b 1)
echo OK Tkinter disponible
REM Paso 3: Dependencias
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (echo ERROR: pip install fallo & pause & exit /b 1)
echo OK Dependencias instaladas
REM Paso 4: Verificar archivos
if not exist main.py (echo ERROR: Falta main.py & pause & exit /b 1)
if not exist src (echo ERROR: Falta carpeta src & pause & exit /b 1)
echo OK Archivos verificados
REM Paso 5: Marcar como instalado
%PY% -c "import sys; sys.path.insert(0, '.'); from src.core import mappings as m; s = m.load_settings(); s['tesseract_installed'] = True; s['first_run'] = False; m.save_settings(s)"
REM Lanzar app
echo.
echo Iniciando Extractor de Recibos...
echo (si se cierra rapido, abre una terminal y ejecuta este .bat desde ahi)
echo.
%PY% main.py
echo.
pause