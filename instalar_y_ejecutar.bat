@echo off
chcp 65001 > nul
title Extractor de Recibos v1.0.6
cd /d "%~dp0"
echo.
echo ============================================================
echo   Extractor de Recibos a Excel v1.0.6
echo ============================================================
echo.
where py >nul 2>nul
if not errorlevel 1 (set "PY=py" & goto pyok)
where python >nul 2>nul
if not errorlevel 1 (set "PY=python" & goto pyok)
echo ERROR: Python no esta instalado.
echo Descargalo desde https://www.python.org/downloads/
echo Tilda "Add Python to PATH" durante la instalacion.
pause
exit /b 1
:pyok
%PY% -c "import tkinter" 2>nul
if errorlevel 1 (echo ERROR: Tkinter no disponible. Reinstala Python con tcl/tk. & pause & exit /b 1)
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (echo ERROR: pip install fallo. & pause & exit /b 1)
%PY% -c "import sys; sys.path.insert(0, '.'); from src.core import mappings as m; s = m.load_settings(); s['tesseract_installed'] = True; s['first_run'] = False; m.save_settings(s)" 2>nul
%PY% main.py
pause
