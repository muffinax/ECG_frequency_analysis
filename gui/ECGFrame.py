import tkinter as tk

from scipy.fft import fftfreq

import localisation
from gui.display_data.AnalysisManager import AnalysisManager
from gui.display_data.DisplayManager import DisplayManager
from gui.display_data.NavigationManager import NavigationManager
from gui.presentation_data_panel.LeadCanvasSet import LeadCanvasSet
from gui.presentation_data_panel.SingleECGCanvas import SingleECGCanvas


class ECGFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager, analysis_manager: AnalysisManager, **kwargs):
        super().__init__(master, **kwargs)
        self.display_manager = display_manager
        self.analysis_manager=analysis_manager
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
            canvas_set = LeadCanvasSet(
                self.scrollable_frame,
                lead,
                self.current_plot_height,
                click_callback=self._handle_graph_click)
            canvas_set.pack(fill=tk.X, expand=False, pady=5)
            self.canvas_sets.append(canvas_set)

    def _on_zoom(self, event):
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

    def update_charts(self, time_axis, signals_dict, fft_data_dict=None, overlap_sec=0.0, is_first=False,
                      is_last=False):

        if fft_data_dict is None:
            fft_data_dict = {}

        current_canvas_leads = [c_set.lead_name for c_set in self.canvas_sets]

        if current_canvas_leads != self.display_manager.displayed_leads:
            self._rebuild_canvas_sets()

        show_fft = self.display_manager.show_frequency_analysis

        for canvas_set in self.canvas_sets:
            lead = canvas_set.lead_name
            canvas_set.toggle_secondary_canvas(show_fft)

            amplitude_data = signals_dict.get(lead)
            fft_data = fft_data_dict.get(lead)

            canvas_set.update_set_data(
                time_axis=time_axis,
                amplitude_data=amplitude_data,
                fft_data=fft_data,
                overlap_sec=overlap_sec,
                is_first=is_first,
                is_last=is_last,
                analysis_start=self.analysis_manager.analysis_start,
                analysis_end=self.analysis_manager.analysis_end,
                analysis_overlap=self.analysis_manager.analysis_overlap,
                is_analysis_active = show_fft
                )

    def _handle_graph_click(self, lead_name, time_start, time_end):
        if not self.display_manager.show_frequency_analysis:
            return

        if self.analysis_manager.fft_time_mode.name == "CUSTOM_TIME":
            if time_end < 0:
                if self.analysis_manager.analysis_start < 0:
                    self.analysis_manager.analysis_start = time_start
                else:
                    if self.analysis_manager.analysis_end < 0:
                        self.analysis_manager.analysis_end = time_start

                        if self.analysis_manager.analysis_start > self.analysis_manager.analysis_end:
                            tmp = self.analysis_manager.analysis_start
                            self.analysis_manager.analysis_start = self.analysis_manager.analysis_end
                            self.analysis_manager.analysis_end = tmp
                    else:
                        # Reset, jeśli były już 2 linie i użytkownik klika 3 raz
                        self.analysis_manager.analysis_start = time_start
                        self.analysis_manager.analysis_end = -1.0

            else:
                self.analysis_manager.analysis_start = time_start
                self.analysis_manager.analysis_end = time_end

        for canvas_set in self.canvas_sets:
            canvas_set.ecg_canvas.apply_analysis(
                analysis_start=self.analysis_manager.analysis_start,
                analysis_end=self.analysis_manager.analysis_end,
                analysis_overlap=self.analysis_manager.analysis_overlap
            )




