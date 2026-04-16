import numpy as np
from .signal_processor import SignalProcessor
from .signal_filter import SignalFilter

class PreprocManager:
    def __init__(self, sampling_frequency: float):
        self.fs = sampling_frequency
        self.processor = SignalProcessor(sampling_frequency)
        self.filter = SignalFilter(sampling_frequency)

    def get_ft_portion(self, data: np.ndarray, start_idx: float, end_idx: float):
        """
        Computes FFT on a window spanning between the R-peaks 
        closest to the requested start and end points.
        """
        return self.processor.get_r_peak_snapped_fft(data, start_idx, end_idx)

    def get_stft_whole(self, data: np.ndarray):
        """
        Computes a beat-synchronous STFT where windows span from R_peak[i] to R_peak[i+2].
        """
        return self.processor.get_beat_synchronous_stft(data)
