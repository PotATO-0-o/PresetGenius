@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   PresetGenius  -  AI synth for Ableton
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv not found. Create it first, see README.md
  pause
  exit /b 1
)

echo Starting AI server on http://127.0.0.1:8901 ...
start "PresetGenius Server" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe -m uvicorn server.main:app --host 127.0.0.1 --port 8901"

echo Waiting until the server is ready...
set /a tries=0
:wait
timeout /t 2 /nobreak >nul
curl.exe -s http://127.0.0.1:8901/health >nul 2>&1
if %errorlevel%==0 goto ready
set /a tries+=1
if %tries% geq 45 (
  echo Server did not start. Check the "PresetGenius Server" window.
  pause
  exit /b 1
)
goto wait

:ready
echo Server is up.

set "VST_SRC=%~dp0synth\vital\plugin\builds\vs17\x64\Release\VST3\Vial.vst3"
set "VST_USER=%LOCALAPPDATA%\Programs\Common\VST3"
set "VST_DIST=%~dp0dist\VST3"
if not exist "%VST_SRC%" (
  echo ERROR: VST3 is not built yet: %VST_SRC%
  pause
  exit /b 1
)

mkdir "%VST_USER%" 2>nul
mkdir "%VST_DIST%" 2>nul
copy /Y "%VST_SRC%" "%VST_USER%\PresetGenius.vst3" >nul
copy /Y "%VST_SRC%" "%VST_DIST%\PresetGenius.vst3" >nul
copy /Y "%VST_SRC%" "%~dp0PresetGenius.vst3" >nul
if exist "D:\Plug-in's\" copy /Y "%VST_SRC%" "D:\Plug-in's\PresetGenius.vst3" >nul

echo Copying into Program Files\Common Files\VST3 (UAC prompt)...
powershell -NoProfile -Command "Start-Process cmd -Verb RunAs -Wait -ArgumentList '/c copy /Y ""%VST_SRC%"" ""%CommonProgramW6432%\VST3\PresetGenius.vst3""'"

echo Installed VST3:
echo   %VST_USER%\PresetGenius.vst3
echo   %CommonProgramW6432%\VST3\PresetGenius.vst3
echo.

echo How to use in Ableton Live:
echo   1. Preferences  -  Plug-Ins
echo   2. Enable "Use VST3 Plug-In System Folders"
echo      If the plugin is missing, add custom folder:
echo      %VST_USER%
echo   3. Rescan plug-ins
echo   4. Browser  -  Instruments  -  PresetGenius
echo   5. Click the STAR next to the preset name
echo      Generate from text  /  Match audio file
echo   6. Play MIDI notes
echo.
echo Keep the "PresetGenius Server" window open while you work.
echo.

set "STANDALONE=%~dp0synth\vital\plugin\builds\vs17\x64\Release\Standalone Plugin\Vial.exe"
if exist "%STANDALONE%" start "" "%STANDALONE%"

echo Standalone is opening so you can try it without Ableton.
pause
