import numpy as np
from dataclasses import dataclass
from typing import Any

@dataclass
class MachineLearningData:
    original_filename: str
    signal_sample_index_start: float
    signal_duration: float
    signal_name: str
    signal_sampling_frequency: float
    signal_fft_freqs: np.ndarray
    signal_fft: np.ndarray
    annotations: list[dict[str, Any]] | None = None
