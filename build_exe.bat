@echo off
REM ────────────────────────────────────────────────────────────
REM  Build ExtractorRecibos.exe using PyInstaller
REM  Result: dist\ExtractorRecibos.exe
REM ────────────────────────────────────────────────────────────

setlocal
chcp 65001 > nul

echo.
echo ============================================================
echo  Extractor de Recibos - Build a .exe
echo ============================================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python no esta instalado o no esta en PATH.
        pause
        exit /b 1
    )
    set "PY=python"
) else (
    set "PY=py"
)

echo [1/3] Instalando dependencias...
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
%PY% -m pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo [2/3] Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ExtractorRecibos.spec del /q ExtractorRecibos.spec

echo.
echo [3/3] Empaquetando con PyInstaller...
%PY% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "ExtractorRecibos" ^
    --icon "assets\icon.ico" ^
    --version-file "version_info.txt" ^
    --add-data "src;src" ^
    --add-data "assets\icon.ico;assets" ^
    --add-data "assets\icon.png;assets" ^
    --hidden-import "PIL._tkinter_finder" ^
    --collect-all "customtkinter" ^
    --collect-all "pytesseract" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Fallo el empaquetado.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Listo! Ejecutable en: dist\ExtractorRecibos.exe
echo ============================================================
echo.

explorer dist 2>nul
pause
endlocal
