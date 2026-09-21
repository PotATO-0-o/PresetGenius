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

## Структура (планируемая)

```
synth/    — форк Vitalium (C++/JUCE, VST3)
ml/       — модели: audio2preset, text2preset, генерация датасета
server/   — локальный inference-сервер, отдающий .vital-пресеты плагину
docs/     — материалы курсовой
```
