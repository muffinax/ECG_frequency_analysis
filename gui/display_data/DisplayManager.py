from file_manager import ELeadType


class DisplayManager:
    def __init__(self):
        self.displayed_leads: list[ELeadType] = []
        # self.frequency_leads: list[str] = []


        self.show_frequency_analysis: bool = False

    def reset_to_defaults(self, available_leads: list[ELeadType]):
        self.displayed_leads = available_leads.copy()
        self.show_frequency_analysis = False