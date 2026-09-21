@echo off
rem Запуск inference-сервера PresetGenius (для работы AI-меню в плагине)
cd /d "%~dp0.."
.venv\Scripts\python.exe -m uvicorn server.main:app --port 8901
