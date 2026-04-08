import tkinter as tk

import localisation
from gui.display_data.DisplayManager import DisplayManager


class DetailsFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager, **kwargs):
        super().__init__(master, **kwargs)

        frequency_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_frequency_label"),
                              font=("Arial", 12))
        self.fragment_width_label = tk.Label(self, text=localisation.name_resolver.get("parameters_fragment_window_width_label"),
                                        font=("Arial", 12))
        self.overlay_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_overlay_label"),
                                      font=("Arial", 12))
        self.start_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_start_label"),
                                        font=("Arial", 12))

        frequency_label.pack(pady=10)
        self.fragment_width_label.pack(pady=10)
        self.overlay_label.pack(pady=10)
        self.start_label.pack(pady=10)