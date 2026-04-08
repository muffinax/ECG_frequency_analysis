import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, stft

class SignalProcessor:
    def __init__(self, sampling_frequency: float):
        self.fs = sampling_frequency
        self.nyquist = 0.5 * self.fs

    # Filtr górnoprzepustowy (Butterworth)
    def apply_highpass(self, data: np.ndarray, cutoff: float = 0.5, order: int = 4) -> np.ndarray:
        normal_cutoff = cutoff / self.nyquist
        b, a = butter(N=order, Wn=normal_cutoff, btype='highpass', analog=False)
        return filtfilt(b, a, data)

    # Filtr dolnoprzepustowy (Butterworth)
    def apply_lowpass(self, data: np.ndarray, cutoff: float = 40.0, order: int = 4) -> np.ndarray:
        normal_cutoff = cutoff / self.nyquist
        b, a = butter(N=order, Wn=normal_cutoff, btype='lowpass', analog=False)
        return filtfilt(b, a, data)

    # Filtr pasmozaporowy
    def apply_notch(self, data: np.ndarray, cutoff: float = 50.0, quality_factor: float = 30.0) -> np.ndarray:
        b, a = iirnotch(w0=cutoff, Q=quality_factor, fs=self.fs)
        return filtfilt(b, a, data)

    def preprocess_ecg(self, data: np.ndarray, powerline_freq: float = 50.0, ) -> np.ndarray:
        filtered = self.apply_highpass(data, cutoff=0.5)
        filtered = self.apply_notch(filtered, cutoff=powerline_freq)
        filtered = self.apply_lowpass(filtered, cutoff=100.0)
        return filtered

    def get_stft(self, data: np.ndarray, window_size_sec: float = 2.0, overlap_factor: float = 0.5):
        nperseg = int(window_size_sec * self.fs)
        noverlap = int(nperseg * overlap_factor)
        
        # Wylicznianie STFT
        f, t, Zxx = stft(x=data, fs=self.fs, nperseg=nperseg, noverlap=noverlap)
        
        # Wyciągniecię "mocy" z danych (to co nas obchodzi)
        magnitude = np.abs(Zxx)
        
        return f, t, magnitude
