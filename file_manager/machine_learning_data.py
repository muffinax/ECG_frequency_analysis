import numpy as np
from dataclasses import dataclass
from typing import Any

@dataclass
class MachineLearningData:
    original_filename: str
    signal_sample_index_start: int
    signal_duration: int
    signal_name: str
    signal_sampling_frequency: float
    signal_fft: np.ndarray
    annotations: list[dict[str, Any]] | None = None
