@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  call "%~dp0Setup-AI.cmd"
  if errorlevel 1 (
    echo Сервер не запущен: сначала нужна установка библиотек ИИ.
    pause
    exit /b 1
  )
)

curl.exe -s -m 2 http://127.0.0.1:8901/health >nul 2>&1
if %errorlevel%==0 (
  echo Сервер ИИ уже работает: http://127.0.0.1:8901
  exit /b 0
)

echo Запуск сервера ИИ. Это окно нужно оставить открытым.
echo Первый запрос в плагине может занять до минуты.
echo.
".venv\Scripts\python.exe" -m uvicorn server.main:app --host 127.0.0.1 --port 8901
pause
