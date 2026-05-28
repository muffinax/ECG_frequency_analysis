import tkinter as tk

from controllers.FileController import FileController
from controllers.NavigationController import NavigationController
from controllers.AIController import AIController

from file_manager import FileManager, EAnnotationOrigin
from processor.preproc_manager import PreprocManager
from display_data.DisplayManager import DisplayManager
from display_data.NavigationManager import NavigationManager
from display_data.AnalysisManager import AnalysisManager

# from gui.MainWindow import MainWindow


class MainController:
    def __init__(self, root: tk.Tk):
        # Models
        self.file_manager = FileManager()
        self.preproc_manager = None
        self.display_manager = DisplayManager()
        self.navigation_manager = NavigationManager()
        self.analysis_manager = AnalysisManager()

        # Sub controllers
        self.file_ctrl = FileController(self)
        self.nav_ctrl = NavigationController(self)
        self.ai_ctrl = AIController(self)

        # View
        # self.view = MainWindow(master=root, controller=self)
        self.view = None

    def refresh_view(self):
        """
        Main method to refresh the entire view based on the current state of the
        file manager, display manager, navigation manager, and analysis manager.
        """
        if not self.view or not self.file_manager.opened():
            return

        fs = self.file_manager.sampling_frequency

        # KROK 1: Rozpakowanie danych bezpośrednio do zmiennych (bez słowników)
        from_sample, to_sample, time_axis = self._prepare_time_axis(fs)

        signals_to_draw = self._prepare_signals(from_sample, to_sample)
        fft_dict_to_draw = self._prepare_fft_data(fs)

        # Rozpakowujemy dokładnie 5 list z adnotacjami
        all_in_window, win_time, win_ai, all_time, all_ai = self._prepare_annotations(from_sample, to_sample)

        # KROK 2: Wysłanie czystych zmiennych do Widoku (GUI)
        self.view.render_tables(
            all_time_anns=all_time,
            all_ai_anns=all_ai,
            win_time_anns=win_time,
            win_ai_anns=win_ai,
            fs=fs
        )

        self.view.render_charts(
            time_axis=time_axis,
            signals_dict=signals_to_draw,
            fft_data_dict=fft_dict_to_draw,
            overlap_sec=self.navigation_manager.overlap_sec,
            is_first=self.navigation_manager.is_first_window(),
            is_last=self.navigation_manager.is_last_window(),
            all_anns_in_window=all_in_window,
            fs=fs
        )

        self.view.update_navigation_time(self.navigation_manager.get_current_time_string())
        self.view.update_header(self.file_manager)

    # ========================================================
    # METODY PRYWATNE (Pomocnicy przygotowujący dane)
    # ========================================================
    def _prepare_time_axis(self, fs: float):
        from_sample = int(round(self.navigation_manager.current_sample))
        window_samples = int(round(self.navigation_manager.window_size_sec * fs))
        to_sample = int(min(from_sample + window_samples, self.navigation_manager.total_samples))

        time_axis = self.file_manager.get_time_axis(from_sample=from_sample, to_sample=to_sample)
        return from_sample, to_sample, time_axis

    def _prepare_signals(self, from_sample: int, to_sample: int):
        signals = {}
        for lead in self.display_manager.displayed_leads:
            signals[lead] = self.file_manager.get_signal(
                channel=lead,
                from_sample=from_sample,
                to_sample=to_sample
            )
        return signals

    def _prepare_fft_data(self, fs: float):
        ffts = {}
        if not self.display_manager.show_frequency_analysis or not self.preproc_manager:
            return ffts

        if self.analysis_manager.analysis_start < 0 or self.analysis_manager.analysis_end < 0:
            return ffts

        start_idx = int(round(self.analysis_manager.analysis_start * fs))
        end_idx = int(round(self.analysis_manager.analysis_end * fs))

        for lead in self.display_manager.displayed_leads:
            full_signal = self.file_manager.get_signal(channel=lead)
            try:
                result = self.preproc_manager.get_ft_portion(full_signal, start_idx, end_idx)
                if len(result) == 4:
                    freqs, mags, a_start, a_end = result
                    ffts[lead] = (freqs, mags, a_start / fs, a_end / fs)
                else:
                    ffts[lead] = result
            except Exception as e:
                print(f"Ostrzeżenie FFT dla {lead}: {e}")
                ffts[lead] = None

        return ffts

    def _prepare_annotations(self, from_sample: int, to_sample: int):
        # 1. Pobieramy bazowe listy
        all_in_window = self.file_manager.get_annotations(from_sample=from_sample, to_sample=to_sample)
        all_overall = self.file_manager.annotations

        # 2. Wycinamy to, co potrzebne
        win_time = [a for a in all_in_window if a.annotation_origin != EAnnotationOrigin.ANALYSIS]
        win_ai = [a for a in all_in_window if a.annotation_origin == EAnnotationOrigin.ANALYSIS]

        all_time = [a for a in all_overall if a.annotation_origin != EAnnotationOrigin.ANALYSIS]
        all_ai = [a for a in all_overall if a.annotation_origin == EAnnotationOrigin.ANALYSIS]

        # Zwracamy po prostu 5 oddzielnych wartości (jako krotkę)
        return all_in_window, win_time, win_ai, all_time, all_ai