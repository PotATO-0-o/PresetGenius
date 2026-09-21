"""
Генератор осмысленных случайных пресетов Vital через Vita.

Полностью случайные значения всех 772 параметров дают шум, поэтому
рандомизируется курируемое подмножество в музыкальных диапазонах:
осцилляторы, фильтр, огибающие, LFO-модуляции и эффекты.

Диапазоны задаются в нормализованном виде [0..1] и отображаются на
фактический (min, max) параметра, считанный из движка.
"""
import numpy as np

# (имя параметра, нижняя и верхняя граница в долях полного диапазона)
CONTINUOUS = {
    "osc_1_wave_frame":      (0.0, 1.0),
    "osc_1_unison_detune":   (0.0, 0.6),
    "osc_1_level":           (0.6, 1.0),
    "osc_1_distortion_amount": (0.0, 0.8),
    "osc_1_spectral_morph_amount": (0.0, 0.8),
    "osc_2_wave_frame":      (0.0, 1.0),
    "osc_2_unison_detune":   (0.0, 0.6),
    "osc_2_level":           (0.3, 0.9),
    "filter_1_cutoff":       (0.25, 0.95),
    "filter_1_resonance":    (0.0, 0.7),
    "filter_1_drive":        (0.0, 0.5),
    "env_1_attack":          (0.0, 0.45),
    "env_1_decay":           (0.3, 0.8),
    "env_1_sustain":         (0.0, 1.0),
    "env_1_release":         (0.15, 0.7),
    "env_2_attack":          (0.0, 0.5),
    "env_2_decay":           (0.3, 0.8),
    "env_2_sustain":         (0.0, 0.8),
    "lfo_1_frequency":       (0.3, 0.8),
    "chorus_dry_wet":        (0.0, 0.6),
    "delay_dry_wet":         (0.0, 0.4),
    "reverb_dry_wet":        (0.0, 0.5),
    "distortion_drive":      (0.0, 0.6),
}

DISCRETE = {
    "osc_1_unison_voices": [1, 1, 2, 4, 8],   # повторы = веса
    "osc_2_unison_voices": [1, 1, 2, 4],
    "osc_1_distortion_type": None,            # None = весь диапазон
    "osc_1_spectral_morph_type": None,
    "filter_1_model": None,
    "filter_1_style": None,
}

TOGGLES = {          # имя: вероятность включения
    "osc_1_on": 1.0,
    "osc_2_on": 0.6,
    "filter_1_on": 0.85,
    "chorus_on": 0.35,
    "delay_on": 0.25,
    "reverb_on": 0.5,
    "distortion_on": 0.2,
}

TRANSPOSE_CHOICES = [0, 0, 0, -12, 12, -7, 7]

# (источник, приёмник, диапазон силы модуляции)
MOD_ROUTINGS = [
    ("env_2", "filter_1_cutoff", (0.2, 0.8), 0.7),
    ("lfo_1", "filter_1_cutoff", (0.05, 0.4), 0.4),
    ("lfo_1", "osc_1_wave_frame", (0.1, 0.6), 0.4),
    ("lfo_1", "osc_1_tune", (0.005, 0.03), 0.15),
    ("env_3", "osc_1_wave_frame", (0.2, 0.8), 0.3),
]


def _set_frac(synth, name, frac):
    """Установить параметр по доле его полного диапазона."""
    info = synth.get_control_details(name)
    synth.get_controls()[name].set(info.min + frac * (info.max - info.min))


def randomize(synth, rng: np.random.Generator):
    """Применяет случайный пресет к synth (начиная с init-пресета)."""
    synth.load_init_preset()
    controls = synth.get_controls()

    for name, prob in TOGGLES.items():
        controls[name].set(1.0 if rng.random() < prob else 0.0)

    for name, (lo, hi) in CONTINUOUS.items():
        _set_frac(synth, name, rng.uniform(lo, hi))

    for name, choices in DISCRETE.items():
        info = synth.get_control_details(name)
        if choices is None:
            controls[name].set(float(rng.integers(int(info.min), int(info.max) + 1)))
        else:
            controls[name].set(float(rng.choice(choices)))

    for osc in ("osc_1", "osc_2"):
        controls[f"{osc}_transpose"].set(float(rng.choice(TRANSPOSE_CHOICES)))

    # LFO в режиме секунд, не темпа
    controls["lfo_1_sync"].set(0.0)

    mod_idx = 1
    for source, dest, (lo, hi), prob in MOD_ROUTINGS:
        if rng.random() < prob and synth.connect_modulation(source, dest):
            controls[f"modulation_{mod_idx}_amount"].set(rng.uniform(lo, hi))
            mod_idx += 1

    return synth.to_json()


# Параметры, которые дооптимизирует CMA-ES (непрерывные, в долях диапазона)
OPT_PARAMS = [
    "osc_1_wave_frame", "osc_1_unison_detune", "osc_1_level",
    "osc_1_distortion_amount", "osc_1_spectral_morph_amount",
    "osc_2_wave_frame", "osc_2_level",
    "filter_1_cutoff", "filter_1_resonance", "filter_1_drive",
    "env_1_attack", "env_1_decay", "env_1_sustain", "env_1_release",
    "lfo_1_frequency", "reverb_dry_wet", "distortion_drive",
]


def get_opt_vector(synth):
    """Текущие значения OPT_PARAMS в долях диапазона [0..1]."""
    vec = []
    controls = synth.get_controls()
    for name in OPT_PARAMS:
        info = synth.get_control_details(name)
        vec.append((controls[name].value() - info.min) / (info.max - info.min))
    return np.array(vec)


def set_opt_vector(synth, vec):
    for name, frac in zip(OPT_PARAMS, np.clip(vec, 0.0, 1.0)):
        _set_frac(synth, name, float(frac))
