@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo   PresetGenius  -  установка библиотек ИИ
echo ============================================
echo.

if exist ".venv\Scripts\python.exe" (
  echo Библиотеки уже установлены.
  echo Чтобы поставить заново, удалите папку .venv и запустите этот файл ещё раз.
  exit /b 0
)

set "PY="
for /f "delims=" %%I in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%I"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PY=%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined PY if exist "%ProgramFiles%\Python311\python.exe" set "PY=%ProgramFiles%\Python311\python.exe"

if not defined PY (
  echo Python 3.11 не найден. Скачиваю установщик...
  if not exist "%~dp0redist" mkdir "%~dp0redist"
  curl.exe -L --fail -o "%~dp0redist\python-3.11.9-amd64.exe" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
  if errorlevel 1 (
    echo Не удалось скачать Python 3.11. Проверьте интернет.
    exit /b 1
  )
  "%~dp0redist\python-3.11.9-amd64.exe" /quiet InstallAllUsers=0 PrependPath=0 Include_pip=1 Include_launcher=1 Include_test=0 Shortcuts=0
  if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PY=%LocalAppData%\Programs\Python\Python311\python.exe"
)

if not defined PY (
  echo Не удалось найти Python 3.11 после установки.
  exit /b 1
)

echo Python: %PY%
echo.
echo Создание окружения и загрузка библиотек. Это займёт несколько минут...
"%PY%" -m venv "%~dp0.venv"
if errorlevel 1 exit /b 1

"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
"%~dp0.venv\Scripts\pip.exe" install "setuptools<81" wheel numpy
"%~dp0.venv\Scripts\pip.exe" install crepe --no-build-isolation
"%~dp0.venv\Scripts\pip.exe" install -r "%~dp0requirements-ai.txt"
if errorlevel 1 (
  echo.
  echo Установка библиотек не удалась. Проверьте интернет и запустите Setup-AI.cmd ещё раз.
  exit /b 1
)

echo.
echo Загрузка модели CLAP...
"%~dp0.venv\Scripts\python.exe" -c "from transformers import ClapModel, ClapProcessor; ClapModel.from_pretrained('laion/clap-htsat-unfused'); ClapProcessor.from_pretrained('laion/clap-htsat-unfused')"

echo.
echo Готово. Можно запускать PresetGenius.
exit /b 0
