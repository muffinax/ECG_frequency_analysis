import numpy as np
from scipy.signal import stft, find_peaks

class SignalProcessor:
    def __init__(self, sampling_frequency: float):
        self.fs = sampling_frequency

    def detect_r_peaks(self, data: np.ndarray, min_distance_sec: float = 0.4) -> np.ndarray:
        squared_data = np.square(data)
        distance_samples = int(min_distance_sec * self.fs)
        prominence_threshold = np.mean(squared_data) * 2 
        
        peaks, _ = find_peaks(squared_data, distance=distance_samples, prominence=prominence_threshold)
        return peaks

    def get_r_peak_snapped_fft(self, data: np.ndarray, start_point: float, end_point: float):
        """Finds closest R-peaks to the given indices and computes FFT between them."""
        r_peaks = self.detect_r_peaks(data)
        
        if len(r_peaks) < 2:
            raise ValueError("Not enough R-peaks detected.")

        # Find the R-peaks closest to the requested start and end points
        closest_start_peak = r_peaks[np.argmin(np.abs(r_peaks - start_point))]
        closest_end_peak = r_peaks[np.argmin(np.abs(r_peaks - end_point))]

        # Ensure correct ordering in case the points were too close or swapped
        actual_start_idx = min(closest_start_peak, closest_end_peak)
        actual_end_idx = max(closest_start_peak, closest_end_peak)

        if actual_start_idx == actual_end_idx:
            raise ValueError("Start and end points snapped to the same R-peak.")

        segment = data[actual_start_idx:actual_end_idx]
        
        # Apply window and FFT
        window = np.hanning(len(segment))
        segment_windowed = segment * window
        
        fft_vals = np.fft.rfft(segment_windowed)
        freqs = np.fft.rfftfreq(len(segment), 1 / self.fs)
        
        return freqs, fft_vals, actual_start_idx, actual_end_idx

    def get_beat_synchronous_stft(self, data: np.ndarray):
        """Computes STFT overlapping between R_peak[i] and R_peak[i+2]."""
        r_peaks = self.detect_r_peaks(data)
        
        if len(r_peaks) < 3:
            raise ValueError("Not enough R-peaks detected to form beat-synchronous windows.")

        max_len = 0
        for i in range(len(r_peaks) - 2):
            window_len = r_peaks[i+2] - r_peaks[i]
            if window_len > max_len:
                max_len = window_len
                
        nfft = int(2 ** np.ceil(np.log2(max_len)))
        
        complex_stft = []
        times = []

        for i in range(len(r_peaks) - 2):
            start_idx = r_peaks[i]
            end_idx = r_peaks[i+2]
            
            segment = data[start_idx:end_idx]
            
            window = np.hanning(len(segment))
            segment_windowed = segment * window
            
            fft_vals = np.fft.rfft(segment_windowed, n=nfft)
            complex_stft.append(fft_vals)
            times.append(((start_idx + end_idx) / 2) / self.fs)
            
        freqs = np.fft.rfftfreq(nfft, 1 / self.fs)
        
        # Zlepienie wyników zespolonych w macierz
        stft_matrix = np.column_stack(complex_stft) 
        
        return freqs, np.array(times), stft_matrix
