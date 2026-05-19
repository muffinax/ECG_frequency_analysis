import numpy as np
from .signal_processor import SignalProcessor
from .signal_filter import SignalFilter
from file_manager import MachineLearningData

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

    def get_stft_whole(self, data: np.ndarray, filename: str, signal_name: str) -> list[MachineLearningData]:
        """
        Computes a beat-synchronous STFT where windows span from R_peak[i] to R_peak[i+2].
        Returns a list of MachineLearningData objects, one for each FFT window.
        """
        freqs, start_times, durations, stft_matrix = self.processor.get_beat_synchronous_stft(data)
        
        ml_data_list = []
        num_windows = stft_matrix.shape[1] 
        
        for i in range(num_windows):
            window_fft = stft_matrix[:, i]
            
            ml_data = MachineLearningData(
                original_filename=filename,
                signal_name=signal_name,

                signal_sampling_frequency=self.fs,
                signal_fft_freqs=freqs,
                signal_fft=window_fft,
                
                signal_sample_index_start=start_times[i],
                signal_duration=durations[i]

            )
            
            ml_data_list.append(ml_data)
            
        return ml_data_list
