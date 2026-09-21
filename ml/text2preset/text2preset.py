"""
Текст -> пресет Vital: CLAP-retrieval по банку + опциональная CMA-ES-дооптимизация.

Запуск:
  python ml/text2preset/text2preset.py "warm analog sub bass" --topk 5
  python ml/text2preset/text2preset.py "dark evolving pad" --optimize
"""
import argparse
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clap_util
import vital_random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BANK_DIR = os.path.join(ROOT, "ml", "output", "bank")
OUT_ROOT = os.path.join(ROOT, "ml", "output")


def load_bank():
    emb = np.load(os.path.join(BANK_DIR, "embeddings.npy"))
    with open(os.path.join(BANK_DIR, "presets.jsonl"), encoding="utf-8") as f:
        presets = [json.loads(line)["preset"] for line in f]
    with open(os.path.join(BANK_DIR, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    return emb, presets, meta


def render_mono(synth, meta):
    audio = np.asarray(
        synth.render(meta["midi_note"], 0.8, meta["note_dur"], meta["render_dur"]),
        dtype=np.float32,
    ).mean(axis=0)
    peak = np.abs(audio).max()
    return audio / max(peak, 1.0)


def optimize_cmaes(synth, text_emb, meta, iterations=15, popsize=8, sigma=0.15):
    """Дожимаем лучший пресет: CMA-ES максимизирует CLAP-сходство с текстом."""
    import cma

    x0 = vital_random.get_opt_vector(synth)
    es = cma.CMAEvolutionStrategy(x0, sigma, {
        "popsize": popsize, "bounds": [0.0, 1.0], "verbose": -9, "seed": 1,
    })
    best_json, best_sim = synth.to_json(), -1.0

    for it in range(iterations):
        solutions = es.ask()
        audios = []
        for x in solutions:
            vital_random.set_opt_vector(synth, x)
            audios.append(render_mono(synth, meta))
        sims = clap_util.embed_audio(audios) @ text_emb
        es.tell(solutions, (-sims).tolist())

        i_best = int(np.argmax(sims))
        if sims[i_best] > best_sim:
            best_sim = float(sims[i_best])
            vital_random.set_opt_vector(synth, solutions[i_best])
            best_json = synth.to_json()
        print(f"  CMA-ES iter {it + 1}/{iterations}: sim = {best_sim:.4f}")

    return best_json, best_sim


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--topk", type=int, default=5)
    parser.add_argument("--optimize", action="store_true",
                        help="CMA-ES-дооптимизация лучшего кандидата")
    parser.add_argument("--iters", type=int, default=15)
    args = parser.parse_args()

    import vita
    synth = vita.Synth()
    synth.set_sample_rate(clap_util.SAMPLE_RATE)

    emb, presets, meta = load_bank()
    text_emb = clap_util.embed_text([args.prompt])[0]
    sims = emb @ text_emb
    order = np.argsort(-sims)[: args.topk]

    slug = re.sub(r"[^a-z0-9]+", "_", args.prompt.lower()).strip("_")[:40]
    out_dir = os.path.join(OUT_ROOT, f"query_{slug}")
    os.makedirs(out_dir, exist_ok=True)

    print(f'Запрос: "{args.prompt}"')
    for rank, idx in enumerate(order, start=1):
        preset_json = presets[idx]
        assert synth.load_json(preset_json)
        with open(os.path.join(out_dir, f"rank{rank}.vital"), "w", encoding="utf-8") as f:
            f.write(preset_json)
        sf.write(os.path.join(out_dir, f"rank{rank}.wav"),
                 render_mono(synth, meta), clap_util.SAMPLE_RATE)
        print(f"  rank {rank}: sim = {sims[idx]:.4f}")

    if args.optimize:
        print("Дооптимизация лучшего кандидата (CMA-ES)...")
        assert synth.load_json(presets[order[0]])
        best_json, best_sim = optimize_cmaes(
            synth, text_emb, meta, iterations=args.iters
        )
        with open(os.path.join(out_dir, "optimized.vital"), "w", encoding="utf-8") as f:
            f.write(best_json)
        assert synth.load_json(best_json)
        sf.write(os.path.join(out_dir, "optimized.wav"),
                 render_mono(synth, meta), clap_util.SAMPLE_RATE)
        print(f"[OK] optimized.vital: sim {sims[order[0]]:.4f} -> {best_sim:.4f}")

    print(f"[OK] Результаты: {out_dir}")


if __name__ == "__main__":
    main()
