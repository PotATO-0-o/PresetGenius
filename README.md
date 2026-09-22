# PresetGenius

Синтезатор для Windows: пресет собирается по текстовому описанию или по загруженному звуку. Форматы — **Standalone** и **VST3** (Ableton Live и другие DAW).

[Скачать установщик](https://github.com/PotATO-0-o/PresetGenius/raw/main/installer/output/PresetGenius-Setup-1.0.0.exe) · [Релиз](https://github.com/PotATO-0-o/PresetGenius/releases/tag/v1.0.0)

## Установка

Запустите `PresetGenius-Setup-1.0.0.exe` и выберите, что ставить:

| Вариант | Что появляется |
| --- | --- |
| Standalone и VST3 | программа и плагин |
| Только Standalone | `PresetGenius.exe` |
| Только VST3 | плагин для DAW |

Нужны права администратора: VST3 кладётся в `C:\Program Files\Common Files\VST3`. Сервер, который считает пресет, ставится вместе с программой. Библиотеки для него (около 2 ГБ) скачиваются в конце установки, если оставить эту галочку. Без интернета этот шаг можно пропустить и запустить `Setup-AI.cmd` позже.

## Как пользоваться

1. Откройте **PresetGenius** из меню Пуск. Сервер запустится сам. Если стоит только VST3, сначала откройте **PresetGenius AI Server**.
2. В Ableton: **Preferences → Plug-Ins → Rescan**, затем инструмент **PresetGenius** на MIDI-трек.
3. Справа от имени пресета нажмите звезду:
   - **Generate from text** — описание, например `warm analog sub bass`
   - **Generate from text (optimized)** — дольше, ближе к описанию
   - **Match audio file** — WAV, MP3, FLAC
4. Играйте ноты. Окно сервера не закрывайте.

Первый запрос после старта может занять до минуты. Волновые таблицы лежат в `Документы\Vial\Wavetables`.

## Сборка из исходников

Нужны Visual Studio 2022 Build Tools, Python 3.11 и [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```powershell
git clone --recurse-submodules https://github.com/PotATO-0-o/PresetGenius.git
cd PresetGenius
py -3.11 -m venv .venv
.venv\Scripts\pip install "setuptools<81" wheel numpy
.venv\Scripts\pip install crepe --no-build-isolation
.venv\Scripts\pip install -r ml/syntheon/requirements.txt vita transformers cma soxr fastapi uvicorn python-multipart
.venv\Scripts\python ml/text2preset/build_bank.py --n 500
```

Плагин:

```powershell
& "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe" `
  synth\vital\plugin\builds\vs17\Vial.sln /p:Configuration=Release /p:Platform=x64 /p:PlatformToolset=v143 `
  /t:"Vial - Shared Code;Vial - VST3;Vial - Standalone Plugin" /m
installer\build.ps1
```

Правки движка относительно [Vital](https://github.com/mtytel/vital) лежат в `synth/presetgenius.patch`.

## Из чего состоит

| Часть | Основа |
| --- | --- |
| Движок и интерфейс | [Vital](https://github.com/mtytel/vital), GPL-3.0 |
| Звук → пресет | [Syntheon](https://github.com/gudgud96/syntheon), Apache-2.0 |
| Текст → пресет | поиск по банку через [CLAP](https://github.com/LAION-AI/CLAP) и донастройка CMA-ES |
| Проверка пресета без DAW | [Vita](https://github.com/DBraun/Vita) |

```
installer/     установщик
server/        локальный сервер пресетов, порт 8901
ml/text2preset текст → пресет
ml/syntheon    звук → пресет
synth/vital    исходники синтезатора
```

## Лицензия

Движок — GPL-3.0, поэтому сборка PresetGenius распространяется на тех же условиях. Текст лицензии: `synth/vital/LICENSE`. Syntheon — Apache-2.0, файл `ml/syntheon/LICENSE`.
