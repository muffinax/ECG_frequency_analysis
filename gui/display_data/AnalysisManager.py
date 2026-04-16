from enum import Enum, auto

class FFTTimeFrameMode(Enum):
    R_TO_R = auto()
    CUSTOM_TIME = auto()

FFT_MODE_LABELS = {
    FFTTimeFrameMode.R_TO_R: "enum_fft_frame_mode_r",
    FFTTimeFrameMode.CUSTOM_TIME: "enum_fft_frame_mode_custom"
}

class InterferenceFilter(Enum):
    NONE = 0
    HZ_50 = 50
    HZ_60 = 60

INTERFERENCE_FILTER_LABELS = {
    InterferenceFilter.NONE: "enum_interfefence_filter_none",
    InterferenceFilter.HZ_50: "enum_interfefence_filter_50",
    InterferenceFilter.HZ_60: "enum_interfefence_filter_60"
}

class AnalysisManager:
    def __init__(self):
        self.fft_time_mode = FFTTimeFrameMode.CUSTOM_TIME
        self.interference_filter = InterferenceFilter.NONE

        self.analysis_start = -1.0
        self.analysis_end = -1.0
        self.analysis_overlap = 0.3
        self.amplitude = 1.0

    def reset_to_defaults(self):
        self.fft_time_mode = FFTTimeFrameMode.CUSTOM_TIME
        self.interference_filter = InterferenceFilter.NONE

        self.analysis_start = -1.0
        self.analysis_end = -1.0
        self.analysis_overlap = 0.3
        self.amplitude = 2