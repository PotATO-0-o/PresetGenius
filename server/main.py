"""
Inference-сервер PresetGenius.

Плагин (или любой клиент) шлёт звук или текст — сервер возвращает
готовый .vital-пресет (JSON). ML работает вне реального времени,
поэтому аудиопоток плагина не блокируется.

Запуск:  .venv\Scripts\python -m uvicorn server.main:app --port 8901
Docs:    http://127.0.0.1:8901/docs
"""
import json
import os
import shutil
import sys
import tempfile

import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHEON_DIR = os.path.join(ROOT, "ml", "syntheon")
TEXT2PRESET_DIR = os.path.join(ROOT, "ml", "text2preset")
sys.path.insert(0, SYNTHEON_DIR)
sys.path.insert(0, TEXT2PRESET_DIR)

app = FastAPI(title="PresetGenius", version="0.1.0")

_bank = None  # (embeddings, presets, meta) — лениво, чтобы старт был быстрым


def get_bank():
    global _bank
    if _bank is None:
        import text2preset as t2p
        _bank = t2p.load_bank()
    return _bank


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/audio2preset")
async def audio2preset(file: UploadFile = File(...)):
    """WAV -> .vital-пресет (Syntheon)."""
    from syntheon import infer_params

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "input.wav")
        with open(wav_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Syntheon пишет результат в cwd и грузит чекпоинты по относительным путям
        cwd = os.getcwd()
        os.chdir(SYNTHEON_DIR)
        try:
            out_file, eval_dict = infer_params(wav_path, "vital", enable_eval=True)
            with open(out_file, encoding="utf-8") as f:
                preset = json.load(f)
            os.remove(out_file)
        finally:
            os.chdir(cwd)

    return JSONResponse({"preset": preset, "loss": eval_dict.get("loss")})


class TextRequest(BaseModel):
    prompt: str
    optimize: bool = False
    iters: int = 10


@app.post("/text2preset")
def text2preset_endpoint(req: TextRequest):
    """Текстовое описание -> .vital-пресет (CLAP retrieval + CMA-ES)."""
    import clap_util
    import text2preset as t2p
    import vita

    emb, presets, meta = get_bank()
    text_emb = clap_util.embed_text([req.prompt])[0]
    sims = emb @ text_emb
    best_idx = int(np.argmax(sims))
    preset_json, sim = presets[best_idx], float(sims[best_idx])

    if req.optimize:
        synth = vita.Synth()
        synth.set_sample_rate(clap_util.SAMPLE_RATE)
        assert synth.load_json(preset_json)
        preset_json, sim = t2p.optimize_cmaes(
            synth, text_emb, meta, iterations=req.iters
        )

    return JSONResponse({"preset": json.loads(preset_json), "similarity": sim})
