"""
Proof of concept: звук -> пресет Vital -> обратный рендер.

1. Берём WAV (по умолчанию — тестовый звук из репозитория Syntheon).
2. Syntheon инферит параметры и сохраняет .vital-пресет.
3. Vita (headless-движок Vital) загружает пресет и рендерит ноту в WAV,
   чтобы можно было на слух сравнить результат с оригиналом.

Запуск:  python ml/poc_sound2preset.py [путь_к_wav]
"""
import os
import sys
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHEON_DIR = os.path.join(ROOT, "ml", "syntheon")
OUTPUT_DIR = os.path.join(ROOT, "ml", "output")

sys.path.insert(0, SYNTHEON_DIR)


def main():
    input_wav = (
        os.path.abspath(sys.argv[1])
        if len(sys.argv) > 1
        else os.path.join(SYNTHEON_DIR, "test", "test_audio", "vital_test_pluck_1.wav")
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Шаг 1: звук -> пресет ---------------------------------------------
    from syntheon import infer_params

    # Syntheon пишет vital_output.vital в cwd; работаем из его папки,
    # чтобы относительные пути к чекпоинтам моделей не сломались.
    os.chdir(SYNTHEON_DIR)
    preset_tmp, eval_dict = infer_params(input_wav, "vital", enable_eval=True)

    preset_path = os.path.join(OUTPUT_DIR, "inferred_preset.vital")
    shutil.move(os.path.join(SYNTHEON_DIR, preset_tmp), preset_path)
    print(f"[OK] Пресет сохранён: {preset_path}")
    print(f"[OK] Spectral loss реконструкции: {eval_dict.get('loss'):.4f}")

    # --- Шаг 2: пресет -> звук (проверка обратной загрузки) ----------------
    import vita
    import soundfile as sf
    import numpy as np

    synth = vita.Synth()
    synth.set_sample_rate(44100)
    with open(preset_path, encoding="utf-8") as f:
        assert synth.load_json(f.read()), "Vital-движок не смог загрузить пресет!"

    audio = synth.render(midi_note=60, midi_velocity=0.8, note_dur=2.0, render_dur=3.0)
    render_path = os.path.join(OUTPUT_DIR, "rendered_from_preset.wav")
    sf.write(render_path, np.asarray(audio).T, 44100)
    print(f"[OK] Пресет загружен движком Vital и отрендерен: {render_path}")

    # Копия исходника рядом — для удобного сравнения на слух.
    shutil.copy(input_wav, os.path.join(OUTPUT_DIR, "original_input.wav"))
    print("[OK] Сквозной пайплайн работает: WAV -> Syntheon -> .vital -> Vital render")


if __name__ == "__main__":
    main()
