import numpy as np
from dataclasses import dataclass

@dataclass
class MachineLearningData:
    original_filename: str
    signal_sample_index_start: int
    signal_duration: int
    signal_name: str
    signal_fft: np.ndarray