"""
Построение банка пресетов: N случайных пресетов Vital -> рендер ноты C3 ->
CLAP-эмбеддинги. Банк — основа retrieval для text2preset.

Запуск:  python ml/text2preset/build_bank.py --n 500
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clap_util
import vital_random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BANK_DIR = os.path.join(ROOT, "ml", "output", "bank")

MIDI_NOTE = 48       # C3 — компромисс: басы и пэды звучат естественно
NOTE_DUR = 2.0
RENDER_DUR = 3.0
BATCH = 16


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    import vita
    synth = vita.Synth()
    synth.set_sample_rate(clap_util.SAMPLE_RATE)
    rng = np.random.default_rng(args.seed)

    os.makedirs(BANK_DIR, exist_ok=True)
    presets, embeddings = [], []
    batch_audio, batch_presets = [], []

    def flush():
        nonlocal batch_audio, batch_presets
        if batch_audio:
            embeddings.append(clap_util.embed_audio(batch_audio))
            presets.extend(batch_presets)
            batch_audio, batch_presets = [], []

    for i in range(args.n):
        preset_json = vital_random.randomize(synth, rng)
        audio = np.asarray(
            synth.render(MIDI_NOTE, 0.8, NOTE_DUR, RENDER_DUR), dtype=np.float32
        ).mean(axis=0)  # стерео -> моно

        peak = np.abs(audio).max()
        if peak < 1e-4:   # тихий/пустой пресет — пропускаем
            continue
        batch_audio.append(audio / max(peak, 1.0))
        batch_presets.append(preset_json)

        if len(batch_audio) == BATCH:
            flush()
            print(f"[{len(presets)}/{args.n}] эмбеддинги посчитаны")

    flush()
    emb = np.concatenate(embeddings, axis=0)

    np.save(os.path.join(BANK_DIR, "embeddings.npy"), emb)
    with open(os.path.join(BANK_DIR, "presets.jsonl"), "w", encoding="utf-8") as f:
        for p in presets:
            f.write(json.dumps({"preset": p}) + "\n")
    with open(os.path.join(BANK_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"midi_note": MIDI_NOTE, "note_dur": NOTE_DUR,
                   "render_dur": RENDER_DUR, "n": len(presets),
                   "seed": args.seed}, f)

    print(f"[OK] Банк: {len(presets)} пресетов, эмбеддинги {emb.shape} -> {BANK_DIR}")


if __name__ == "__main__":
    main()
