"""Factory wavetables for PresetGenius. Vital's GPL source does not include the commercial tables."""
import base64
import json
import os

import numpy as np

N = 2048
FRAMES = 32


def b64(wave: np.ndarray) -> str:
    wave = np.asarray(wave, dtype=np.float32)
    wave = wave - wave.mean()
    peak = np.max(np.abs(wave))
    if peak > 1e-8:
        wave = wave / peak * 0.95
    return base64.b64encode(wave.tobytes()).decode("ascii")


def table(name: str, frames: list[np.ndarray]) -> dict:
    # Позиции кадров — от 0 до 256, иначе морф занимает только начало ручки Wave.
    if len(frames) == 1:
        positions = [0]
    else:
        positions = [int(round(i * 256 / (len(frames) - 1))) for i in range(len(frames))]
    keyframes = []
    for position, frame in zip(positions, frames):
        keyframes.append({"position": position, "wave_data": b64(frame)})
    return {
        "name": name,
        "author": "PresetGenius",
        "version": "1.0.6",
        "remove_all_dc": True,
        "full_normalize": True,
        "groups": [{
            "components": [{
                "type": "Wave Source",
                "interpolation": 0,
                "interpolation_style": 0,
                "keyframes": keyframes,
            }]
        }],
    }


def phase(n=N):
    return np.linspace(0, 2 * np.pi, n, endpoint=False)


def sine(n=N):
    return np.sin(phase(n))


def saw(n=N):
    return 1 - 2 * np.linspace(0, 1, n, endpoint=False)


def square(width=0.5, n=N):
    x = np.linspace(0, 1, n, endpoint=False)
    return np.where(x < width, 1.0, -1.0)


def triangle(n=N):
    x = np.linspace(0, 1, n, endpoint=False)
    return 4 * np.abs(x - 0.5) - 1


def harmonics(amps, n=N):
    t = phase(n)
    wave = np.zeros(n)
    for k, amp in enumerate(amps, start=1):
        wave += amp * np.sin(k * t)
    return wave


def morph(a, b, steps):
    return [(1 - i / (steps - 1)) * a + (i / (steps - 1)) * b for i in range(steps)]


def build() -> dict[str, dict]:
    basic = []
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        if t < 0.33:
            u = t / 0.33
            basic.append((1 - u) * sine() + u * triangle())
        elif t < 0.66:
            u = (t - 0.33) / 0.33
            basic.append((1 - u) * triangle() + u * saw())
        else:
            u = (t - 0.66) / 0.34
            basic.append((1 - u) * saw() + u * square())

    pulse = [square(0.05 + 0.45 * i / (FRAMES - 1)) for i in range(FRAMES)]

    harm = []
    for i in range(FRAMES):
        count = 1 + int(i / (FRAMES - 1) * 24)
        amps = [1.0 / k for k in range(1, count + 1)]
        harm.append(harmonics(amps))

    organ = []
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        organ.append(harmonics([
            1.0,
            0.2 + 0.6 * t,
            0.5 * (1 - t),
            0.15,
            0.4 * t,
            0.1,
            0.05,
            0.2 * t,
        ]))

    formant = []
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        amps = np.exp(-0.5 * ((np.arange(1, 40) - (4 + 18 * t)) / 3.5) ** 2)
        formant.append(harmonics(amps))

    metallic = []
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        amps = [0.0] * 16
        amps[0] = 1.0
        amps[int(2 + t * 10)] = 0.7
        amps[int(4 + t * 8)] = 0.4
        metallic.append(harmonics(amps))

    return {
        "Basic Shapes": table("Basic Shapes", basic),
        "Pulse Width": table("Pulse Width", pulse),
        "Harmonics": table("Harmonics", harm),
        "Organ": table("Organ", organ),
        "Formant": table("Formant", formant),
        "Metallic": table("Metallic", metallic),
        "Sine": table("Sine", [sine()]),
        "Triangle": table("Triangle", [triangle()]),
        "Saw": table("Saw", [saw()]),
        "Square": table("Square", [square()]),
    }


def write_all(folder: str):
    os.makedirs(folder, exist_ok=True)
    for name, data in build().items():
        path = os.path.join(folder, name + ".vitaltable")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        print(path)


if __name__ == "__main__":
    dest = os.environ.get("WAVETABLE_DIR")
    if not dest:
        raise SystemExit("Set WAVETABLE_DIR")
    write_all(dest)
