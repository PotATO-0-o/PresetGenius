PresetGenius
============

Синтезатор с генерацией пресета по тексту или по звуку.

Что вы выбрали при установке
----------------------------
- Standalone — программа PresetGenius.exe. Ярлык в меню Пуск.
- VST3 — плагин для Ableton Live и других DAW.
  Файл: C:\Program Files\Common Files\VST3\PresetGenius.vst3

Перед игрой нужен сервер ИИ. Ярлык «PresetGenius» запускает его сам.
Если ставили только VST3, сначала откройте «PresetGenius AI Server» в меню Пуск.

Ableton Live
------------
1. Preferences → Plug-Ins → Rescan.
2. Включите Use VST3 Plug-In System Folders.
3. Instruments → PresetGenius → MIDI-трек.
4. Звезда рядом с именем пресета:
   - Generate from text
   - Generate from text (optimized)
   - Match audio file
5. Играйте ноты. Окно сервера не закрывайте.

Первый запуск скачивает Python 3.11 (если его нет) и библиотеки ИИ
(около 2 ГБ, нужен интернет), если вы отметили это в установщике.
Иначе запустите Setup-AI.cmd в папке установки.
Visual C++ скачивается только если его ещё нет в системе.

Лицензии
--------
Движок синтезатора основан на Vital (GPL-3.0).
Модель звук→пресет — Syntheon (Apache-2.0).
Тексты лицензий лежат в папке licenses.
