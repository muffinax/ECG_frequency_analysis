from enum import Enum, auto

class FFTTimeFrameMode(Enum):
    R_TO_R = auto()
    CUSTOM_TIME = auto()

class InterferenceFilter(Enum):
    NONE = 0
    HZ_50 = 50
    HZ_60 = 60

FILTER_LABELS = {
    InterferenceFilter.NONE: "Bez odfiltrowania",
    InterferenceFilter.HZ_50: "50 Hz",
    InterferenceFilter.HZ_60: "60 Hz"
}

class AnalysisManager:
    def __init__(self):
        self.interference: InterferenceFilter = InterferenceFilter.NONE
        self.analysis_time_mode: FFTTimeFrameMode = FFTTimeFrameMode.CUSTOM_TIME

        self.analysis_start = -1.0
        self.analysis_end = -1.0
        self.analysis_overlap = 0.5

    def reset_to_defaults(self):
        self.interference: InterferenceFilter = InterferenceFilter.NONE
        self.analysis_time_mode: FFTTimeFrameMode = FFTTimeFrameMode.CUSTOM_TIME

        self.analysis_start = -1.0
        self.analysis_end = -1.0
        self.analysis_overlap = 0.5