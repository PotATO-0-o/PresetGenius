@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto server
call "%~dp0Setup-AI.cmd"
if errorlevel 1 goto fail

:server
curl.exe -s -m 2 http://127.0.0.1:8901/health >nul 2>&1
if %errorlevel%==0 goto launch

start "PresetGenius AI" "%~dp0Start-Server.cmd"
set tries=0
:wait
timeout /t 2 /nobreak >nul
curl.exe -s -m 2 http://127.0.0.1:8901/health >nul 2>&1
if %errorlevel%==0 goto launch
set /a tries+=1
if %tries% lss 45 goto wait
echo Сервер ИИ не ответил. Откройте Start-Server.cmd и посмотрите сообщение об ошибке.
pause
exit /b 1

:launch
if not exist "%~dp0PresetGenius.exe" goto vst3only
start "" "%~dp0PresetGenius.exe"
exit /b 0

:vst3only
echo Standalone не установлен. Сервер ИИ запущен — откройте плагин VST3 в Ableton.
pause
exit /b 0

:fail
echo PresetGenius не запущен: не удалось установить библиотеки ИИ.
pause
exit /b 1
