import tkinter as tk

from scipy.fft import fftfreq

import localisation
from gui.display_data.DisplayManager import DisplayManager
from gui.presentation_data_panel.LeadCanvasSet import LeadCanvasSet
from gui.presentation_data_panel.SingleECGCanvas import SingleECGCanvas


class ECGFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager, **kwargs):
        super().__init__(master, **kwargs)
        self.display_manager = display_manager
        self.canvas_sets = []
        self.current_plot_height = 2.5

        self.bg_canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)

        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.bg_canvas.yview)
        self.bg_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bg_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollable_frame = tk.Frame(self.bg_canvas)

        self.canvas_window = self.bg_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.bg_canvas.configure(scrollregion=self.bg_canvas.bbox("all"))
        )

        self.bg_canvas.bind(
            "<Configure>",
            lambda e: self.bg_canvas.itemconfig(self.canvas_window, width=e.width)
        )

        # Obsługa kółka myszy
        self.bg_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.bg_canvas.bind_all("<Control-MouseWheel>", self._on_zoom)  #Windows/MacOS
        self.bg_canvas.bind_all("<Control-Button-4>", self._on_zoom)  #Linux (Scroll Up)
        self.bg_canvas.bind_all("<Control-Button-5>", self._on_zoom)  #Linux (Scroll Down)

    def _on_mousewheel(self, event):
        #(Windows/Mac)
        self.bg_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _rebuild_canvas_sets(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.canvas_sets.clear()

        for lead in self.display_manager.displayed_leads:
            # Przekazujemy zapamiętaną wysokość podczas tworzenia NOWYCH zestawów
            canvas_set = LeadCanvasSet(self.scrollable_frame, lead, self.current_plot_height)
            canvas_set.pack(fill=tk.X, expand=False, pady=5)
            self.canvas_sets.append(canvas_set)

    def _on_zoom(self, event):
        """Obsługuje zdarzenie Ctrl + Scroll do zmiany wysokości wykresów."""
        step = 0.2

        if hasattr(event, 'num') and event.num == 4:  # Linux
            self.current_plot_height += step
        elif hasattr(event, 'num') and event.num == 5:  # Linux
            self.current_plot_height -= step
        elif hasattr(event, 'delta'):
            if event.delta > 0:  # Windows/Mac
                self.current_plot_height += step
            elif event.delta < 0:  # Windows/Mac
                self.current_plot_height -= step

        self.current_plot_height = max(1.0, min(self.current_plot_height, 5.0))

        for canvas_set in self.canvas_sets:
            canvas_set.set_height(self.current_plot_height)

    def update_charts(self, time_axis, signals_dict, secondary_data_dict=None, overlap_sec=0.0, is_first=False,
                      is_last=False):
        if secondary_data_dict is None:
            secondary_data_dict = {}

        current_canvas_leads = [c_set.lead_name for c_set in self.canvas_sets]

        if current_canvas_leads != self.display_manager.displayed_leads:
            self._rebuild_canvas_sets()

        show_fft = self.display_manager.show_frequency_analysis

        for canvas_set in self.canvas_sets:
            lead = canvas_set.lead_name
            canvas_set.toggle_secondary_canvas(show_fft)

            amplitude_data = signals_dict.get(lead)
            analysis_data = secondary_data_dict.get(lead)

            canvas_set.update_set_data(time_axis, amplitude_data, analysis_data, overlap_sec, is_first, is_last)