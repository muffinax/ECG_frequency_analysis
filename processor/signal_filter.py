import numpy as np
from scipy.signal import butter, filtfilt, iirnotch

class SignalFilter:
    def __init__(self, sampling_frequency: float, powerline_freq: float = 50.0, cutoff_min: float = 0.5, cutoff_max: float = 150.0):
        self.nyquist = 0.5 * sampling_frequency
        self.cutoff_min = cutoff_min
        self.cutoff_max = cutoff_max
        self.powerline_freq = powerline_freq

    # Filtr górnoprzepustowy (Butterworth)
    def apply_highpass(self, data: np.ndarray, order: int = 4) -> np.ndarray:
        normal_cutoff = self.cutoff_min / self.nyquist
        b, a = butter(N=order, Wn=normal_cutoff, btype='highpass', analog=False)
        return filtfilt(b, a, data)

    # Filtr dolnoprzepustowy (Butterworth)
    def apply_lowpass(self, data: np.ndarray, order: int = 4) -> np.ndarray:
        normal_cutoff = self.cutoff_max / self.nyquist
        b, a = butter(N=order, Wn=normal_cutoff, btype='lowpass', analog=False)
        return filtfilt(b, a, data)

    # Filtr pasmozaporowy
    def apply_notch(self, data: np.ndarray, quality_factor: float = 30.0) -> np.ndarray:
        b, a = iirnotch(w0=self.powerline_freq, Q=quality_factor, fs=self.fs)
        return filtfilt(b, a, data)
