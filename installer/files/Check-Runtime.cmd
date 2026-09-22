@echo off
setlocal
cd /d "%~dp0"

if exist "%SystemRoot%\System32\vcruntime140.dll" if exist "%SystemRoot%\System32\vcruntime140_1.dll" exit /b 0

echo Visual C++ runtime не найден. Скачиваю...
curl.exe -L --fail -o "%TEMP%\vc_redist.x64.exe" "https://aka.ms/vs/17/release/vc_redist.x64.exe"
if errorlevel 1 exit /b 1
"%TEMP%\vc_redist.x64.exe" /install /quiet /norestart
exit /b 0
