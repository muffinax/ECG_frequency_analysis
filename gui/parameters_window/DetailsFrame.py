import tkinter as tk

import localisation
from display_data import AnalysisManager
from display_data import NavigationManager


class DetailsFrame(tk.Frame):
    def __init__(self, master, analysis_manager: AnalysisManager, navigation_manager: NavigationManager ,**kwargs):
        super().__init__(master, **kwargs)

        self.analysis_manager = analysis_manager
        self.navigation_manager=navigation_manager

        # self.var_fft_mode = tk.StringVar(value=self.analysis_manager.fft_time_mode.name)
        # self.var_filter = tk.StringVar(value=self.analysis_manager.interference_filter.name)

        # overlay_val = str(self.analysis_manager.analysis_overlap)
        amplitude_val = str(self.navigation_manager.amplitude)
        window_time_var = str(self.navigation_manager.window_size_sec)

        # self.var_overlay = tk.StringVar(value=overlay_val)
        self.var_amplitude = tk.StringVar(value=amplitude_val)
        self.var_window_time = tk.StringVar(value=window_time_var)

        self._build_ui()

    def _build_ui(self):
        # self.analysis_label = tk.Label(self, text=localisation.name_resolver.get(
        #     "parameters_analysis_label"), font=("Arial", 14, "bold"))
        # self.analysis_label.pack(pady=(10, 5), anchor="w", fill="x")

        #Choosing how to make "windows"
        # self.fragment_width_label = tk.Label(self, text=localisation.name_resolver.get("parameters_fragment_window_width_label"), font=("Arial", 12))
        # self.fragment_width_label.pack(pady=10)
        #
        # frame_fft_mode = tk.Frame(self)
        # frame_fft_mode.pack(fill="x", padx=15)
        #
        # for mode_enum, lang_key in FFT_MODE_LABELS.items():
        #     rb = tk.Radiobutton(
        #         frame_fft_mode,
        #         text=localisation.name_resolver.get(lang_key),
        #         variable=self.var_fft_mode,
        #         value=mode_enum.name,
        #     )
        #     rb.pack(side=tk.LEFT, padx=15)
        #
        # #Overlay
        # self.overlay_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_overlay_label"), font=("Arial", 12))
        # self.overlay_label.pack(pady=10)
        #
        # overlay_entry = tk.Entry(self, textvariable=self.var_overlay, width=10, justify="center")
        # overlay_entry.pack(pady=2)
        #
        # #Interference
        # self.interference_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_interference_label"), font=("Arial", 12))
        # self.interference_label.pack(pady=10)
        #
        # interference_mode = tk.Frame(self)
        # interference_mode.pack(fill="x", padx=15)
        # for mode_enum, lang_key in INTERFERENCE_FILTER_LABELS.items():
        #     rb = tk.Radiobutton(
        #         interference_mode,
        #         text=localisation.name_resolver.get(lang_key),
        #         variable=self.var_filter,  # POPRAWIONE: było var_fft_mode
        #         value=mode_enum.name
        #     )
        #     rb.pack(side=tk.LEFT, padx=15)

        #Amplitude
        self.amplitude_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_amplitude_label"), font=("Arial", 12))
        self.amplitude_label.pack()

        amplitude_entry = tk.Entry(self, textvariable=self.var_amplitude, width=10, justify="center")
        amplitude_entry.pack(pady=2)

        # Window
        self.window_label = tk.Label(self, text=localisation.name_resolver.get("parameters_window_size_label"),
                                        font=("Arial", 12))
        self.window_label.pack()

        window_entry = tk.Entry(self, textvariable=self.var_window_time, width=10, justify="center")
        window_entry.pack(pady=2)

    def apply_settings(self):
        # selected_mode_str = self.var_fft_mode.get()
        # selected_filter_str = self.var_filter.get()

        # self.analysis_manager.fft_time_mode = FFTTimeFrameMode[selected_mode_str]
        # self.analysis_manager.interference_filter = InterferenceFilter[selected_filter_str]

        # try:
        #     self.analysis_manager.analysis_overlap = float(self.var_overlay.get().replace(',', '.'))
        # except ValueError:
        #     pass

        try:
            self.navigation_manager.amplitude = float(self.var_amplitude.get().replace(',', '.'))
        except ValueError:
            pass

        try:
            new_window_size = float(self.var_window_time.get().replace(',', '.'))

            if new_window_size >= 1.0:
                self.navigation_manager.window_size_sec = new_window_size
        except ValueError:
            pass