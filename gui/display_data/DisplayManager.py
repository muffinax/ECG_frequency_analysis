class DisplayManager:
    def __init__(self):
        self.available_leads: list[str] = []
        self.displayed_leads: list[str] = []
        self.show_frequency_analysis: bool = False

    def reset_to_defaults(self, available_leads: list[str]):
        self.available_leads = available_leads.copy()
        self.displayed_leads = available_leads.copy()
        self.show_frequency_analysis = False