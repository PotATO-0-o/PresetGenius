# PresetGenius

VST3-синтезатор с ИИ-генерацией пресетов по загружаемому звуку или текстовому описанию (в духе Synplant 2 / Genopatch). Курсовой проект.

## Установщик

Готовый файл: [installer/output/PresetGenius-Setup-1.0.0.exe](installer/output/PresetGenius-Setup-1.0.0.exe) (около 16 МБ).
Пересобрать: `installer\build.ps1`.

При установке можно выбрать **Standalone**, **VST3** или оба варианта. Сервер ИИ ставится всегда.
Python 3.11 и библиотеки ИИ (около 2 ГБ) скачиваются при установке, если отметить этот шаг. Нужен интернет.

## Запуск в Ableton

1. Дважды кликните `Start-PresetGenius.bat`.
2. Дождитесь окна **PresetGenius Server** и открытия standalone-синта.
3. В Ableton: **Preferences → Plug-Ins**
   - включите **Use VST3 Plug-In System Folders**
   - или добавьте папку `%LOCALAPPDATA%\Programs\Common\VST3`
   - на этой машине плагин также лежит в `D:\Plug-in's\PresetGenius.vst3`
   - нажмите **Rescan**
4. В браузере инструментов найдите **PresetGenius**, перетащите на MIDI-трек.
5. Нажмите **звезду** справа от имени пресета:
   - **Generate from text** — описание звука
   - **Generate from text (optimized)** — то же + CMA-ES, медленнее
   - **Match audio file** — WAV/MP3
6. Играйте MIDI. Окно сервера не закрывайте.

Первый запрос после старта сервера может занять 15–40 секунд (загрузка CLAP).

## Архитектура

- **Синтезатор** — форк [Vital](https://github.com/mtytel/vital) (GPLv3), собран как **PresetGenius** VST3/Standalone. Пресет — JSON (`.vital`).
- **Звук → пресет** — [Syntheon](https://github.com/gudgud96/syntheon).
- **Текст → пресет** — CLAP retrieval по банку + CMA-ES (метод [CTAG](https://github.com/PapayaResearch/ctag)).
- **Headless-рендер** — [Vita](https://github.com/DBraun/Vita).
- **Плагин → сервер** — HTTP `127.0.0.1:8901` (`/text2preset`, `/audio2preset`).

## Структура

```
Start-PresetGenius.bat   — запуск сервера + установка VST3 + standalone
dist/VST3/               — копия PresetGenius.vst3
synth/vital/             — исходники синта (git submodule)
ml/syntheon/             — вендоренный Syntheon
ml/text2preset/          — текст → пресет
server/                  — FastAPI inference-сервер
```

## Сборка плагина (если меняли C++)

Visual Studio 2022 Build Tools, конфигурация `Release|x64`:

```powershell
& "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe" `
  synth\vital\plugin\builds\vs17\Vial.sln /p:Configuration=Release /p:Platform=x64 `
  /t:Vial_SharedCode,Vial_VST3,Vial_StandalonePlugin /m
```

## Окружение Python

Нужен Python 3.11:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\pip install "setuptools<81" wheel numpy
.venv\Scripts\pip install crepe --no-build-isolation
.venv\Scripts\pip install -r ml/syntheon/requirements.txt vita transformers cma soxr fastapi uvicorn python-multipart
.venv\Scripts\python ml/text2preset/build_bank.py --n 500
```

## Статус

- [x] Звук → пресет → рендер
- [x] Текст → пресет (CLAP + CMA-ES)
- [x] Inference-сервер FastAPI
- [x] VST3 / Standalone PresetGenius с кнопкой AI
- [x] Установка в системную папку VST3 и launcher для Ableton
