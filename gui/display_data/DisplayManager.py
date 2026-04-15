from enum import Enum, auto

class FFTTimeFrameMode(Enum):
    R_TO_R = auto()
    CUSTOM_TIME = auto()

class DisplayManager:
    def __init__(self):
        self.available_leads: list[str] = []
        self.displayed_leads: list[str] = []
        self.show_frequency_analysis: bool = False

        self.analysis_time_mode: FFTTimeFrameMode = FFTTimeFrameMode.CUSTOM_TIME

        self.analysis_start = -1.0
        self.analysis_end = -1.0

    def reset_to_defaults(self, available_leads: list[str]):
        self.available_leads = available_leads.copy()
        self.displayed_leads = available_leads.copy()
        self.show_frequency_analysis = False

        self.analysis_time_mode: FFTTimeFrameMode = FFTTimeFrameMode.CUSTOM_TIME

        self.analysis_start = -1.0
        self.analysis_end = -1.0