# PresetGenius

VST3-синтезатор с ИИ-генерацией пресетов по загружаемому звуку или текстовому описанию (в духе Synplant 2 / Genopatch). Курсовой проект.

## Идея

Пользователь загружает аудиофайл **или** вводит текстовое описание звука — система генерирует пресет для синтезатора, который остаётся только загрузить.

## Архитектура

- **Синтезатор** — форк [Vitalium](https://github.com/DISTRHO/DISTRHO-Ports) (редистрибутируемая сборка open-source синта [Vital](https://github.com/mtytel/vital), GPLv3). Пресет — JSON-файл (`.vital`).
- **Звук → пресет** — [Syntheon](https://github.com/gudgud96/syntheon): инференс параметров Vital по аудио.
- **Текст → пресет** — CLAP text-embedding + retrieval по банку пресетов + CMA-ES-дооптимизация (метод [CTAG](https://github.com/PapayaResearch/ctag), ICML 2024).
- **Headless-рендер** — [Vita](https://github.com/DBraun/Vita): Python-биндинги движка Vital для генерации датасета и оптимизации.
- **Интеграция** — плагин общается с локальным Python-сервером модели (схема [Sound2Synth](https://github.com/Sound2Synth/Sound2Synth)); ML-часть работает вне реального времени.

## Структура

```
synth/vital/             — исходники Vital (git submodule, GPLv3)
ml/syntheon/             — вендоренный Syntheon с нашими фиксами (Apache 2.0)
ml/poc_sound2preset.py   — сквозной PoC: WAV -> Syntheon -> .vital -> рендер Vita
ml/output/               — результаты инференса (не в git)
server/                  — локальный inference-сервер, отдающий .vital-пресеты плагину
docs/                    — материалы курсовой
```

## Окружение

Python 3.11 (не 3.12+: зависимости Syntheon требуют старые setuptools):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\pip install "setuptools<81" wheel numpy
.venv\Scripts\pip install crepe --no-build-isolation
.venv\Scripts\pip install -r ml/syntheon/requirements.txt vita
.venv\Scripts\python ml/poc_sound2preset.py   # сквозная проверка
```

## Статус

- [x] Сквозной пайплайн звук → пресет → рендер работает (spectral loss ~0.11 на тестовом plucke)
- [x] Исправления Syntheon: форма выхода torchcrepe (2D → 1D), обрезка аудио до вычисления признаков в `preprocessor.py`
- [ ] Текст → пресет (CLAP retrieval + CMA-ES, метод CTAG)
- [ ] Inference-сервер (FastAPI)
- [ ] Сборка Vitalium (VST3) и панель загрузки пресетов из сервера
