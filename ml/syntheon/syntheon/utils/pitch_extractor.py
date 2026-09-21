"""
[WIP] Common class for pitch extraction across all synthesizers.
"""

import numpy as np
import os
import torchcrepe
import yaml 

with open(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "../inferencer/vital/config.yaml"
    ), 'r'
) as stream:
    config = yaml.safe_load(stream)


def extract_pitch(signal, sampling_rate, block_size, model_capacity="full"):
    length = signal.shape[-1] // block_size
    f0 = torchcrepe.predict(
        signal, 
        sampling_rate
    )
    # torchcrepe возвращает тензор (1, frames); np.interp ждёт 1-D массив
    f0 = np.asarray(f0.detach().cpu() if hasattr(f0, "detach") else f0).squeeze()

    if f0.shape[-1] != length:
        f0 = np.interp(
            np.linspace(0, 1, length, endpoint=False),
            np.linspace(0, 1, f0.shape[-1], endpoint=False),
            f0,
        )

    return f0