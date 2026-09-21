"""Обёртка над CLAP (laion/clap-htsat-unfused) для текстовых и аудио-эмбеддингов."""
import numpy as np
import torch

MODEL_NAME = "laion/clap-htsat-unfused"
SAMPLE_RATE = 48000  # рабочая частота CLAP

_model = None
_processor = None


def _load():
    global _model, _processor
    if _model is None:
        from transformers import ClapModel, ClapProcessor
        _model = ClapModel.from_pretrained(MODEL_NAME)
        _model.eval()
        _processor = ClapProcessor.from_pretrained(MODEL_NAME)
    return _model, _processor


@torch.no_grad()
def embed_audio(audios: list[np.ndarray]) -> np.ndarray:
    """Список моно-сигналов 48 кГц -> L2-нормированные эмбеддинги (N, 512)."""
    model, processor = _load()
    inputs = processor(audio=audios, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    emb = model.get_audio_features(**inputs).pooler_output  # (N, 512) в общем пространстве
    return torch.nn.functional.normalize(emb, dim=-1).cpu().numpy()


@torch.no_grad()
def embed_text(texts: list[str]) -> np.ndarray:
    model, processor = _load()
    inputs = processor(text=texts, return_tensors="pt", padding=True)
    emb = model.get_text_features(**inputs).pooler_output
    return torch.nn.functional.normalize(emb, dim=-1).cpu().numpy()
