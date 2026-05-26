import os
import sys
import tkinter as tk
import traceback
from tkinter import messagebox

from gui.AnnotationFrame import AnnotationFrame
from gui.display_data.AnalysisManager import AnalysisManager
from gui.display_data.DisplayManager import DisplayManager
from gui.ECGFrame import ECGFrame
from gui.SettingsFrame import SettingsFrame
from gui.display_data.NavigationManager import NavigationManager
from gui.parameters_window.ParametersWindow import ParametersWindow
from gui.HelpWindow import HelpWindow

from file_manager import FileManager
import localisation
from processor.preproc_manager import PreprocManager


class MainWindow:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master

        self.file_manager = FileManager()
        self.preproc_manager = None

        self.display_manager = DisplayManager()
        self.navigation_manager = NavigationManager()
        self.analysis_manager = AnalysisManager()

        if sys.platform == 'win32':
            # Windows
            self.master.state('zoomed')
        elif sys.platform.startswith('linux'):
            # Linux
            self.master.attributes('-zoomed', True)
        else:
            # macOS
            self.master.attributes('-fullscreen', True)

        self.master.title(localisation.name_resolver.get("main_title"))

        # NOWE: Zmienna przechowująca stan Trybu Developera (True/False)
        self.developer_mode_var = tk.BooleanVar(value=False)

        self.__create_menu()

        self.chosen_annotation = -1

        self.frame_annotations = AnnotationFrame(
            master=self.master,
            on_filter_changed_callback=self.update,
            on_annotation_click_callback=self.on_annotation_clicked,
            width=600
        )
        self.frame_annotations.pack_propagate(False)
        self.frame_annotations.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_buttons = SettingsFrame(
            master=self.master,
            navigation_manager=self.navigation_manager,
            display_manager = self.display_manager,
            preproc_manager = self.preproc_manager,
            file_manager = self.file_manager,
            on_update_callback=self.update,
            on_prev_annotation_callback=lambda: self.jump_annotation(-1),
            on_next_annotation_callback=lambda: self.jump_annotation(1),
            height=80
        )
        self.frame_buttons.pack_propagate(False)
        self.frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        # HEADER
        self.frame_header = tk.Frame(self.master, height=50, bg="#f0f0f0", bd=1, relief=tk.RIDGE)
        self.frame_header.pack(side=tk.TOP, fill=tk.X)

        self.label_file_info = tk.Label(self.frame_header, text="Plik: ---", font=("Arial", 10, "bold"), bg="#f0f0f0")
        self.label_file_info.pack(side=tk.LEFT, padx=10, pady=5)
        self.label_patient_name = tk.Label(self.frame_header, text="Pacjent: ---", font=("Arial", 10), bg="#f0f0f0")
        self.label_patient_name.pack(side=tk.LEFT, padx=15, pady=5)

        self.label_date_info = tk.Label(self.frame_header, text="Data: ---", font=("Arial", 10), bg="#f0f0f0")
        self.label_date_info.pack(side=tk.LEFT, padx=15, pady=5)
        self.label_duration_info = tk.Label(self.frame_header, text="Czas trwania: -- [s]", font=("Arial", 10),
                                            bg="#f0f0f0")
        self.label_duration_info.pack(side=tk.LEFT, padx=20, pady=5)
        self.label_fs_info = tk.Label(self.frame_header, text="Fs: --- Hz", font=("Arial", 10), bg="#f0f0f0")
        self.label_fs_info.pack(side=tk.RIGHT, padx=10, pady=5)

        # ECG CHARTS
        self.frame_ecg = ECGFrame(master=self.master, display_manager=self.display_manager,
                                  analysis_manager=self.analysis_manager, on_update_callback=self.update)
        self.frame_ecg.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.master.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __create_menu(self) -> None:
        menu_bar = tk.Menu(master=self.master)

        # MENU: Plik
        self.menu_file = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_file"), menu=self.menu_file)

        self.menu_file.add_command(
            label=localisation.name_resolver.get("menubar_file_open"),
            command=self.open_file_dialog)
        self.menu_file.add_command(
            label=localisation.name_resolver.get("menubar_file_save"),
            command=self.save_file)
        self.menu_file.add_command(
            label=localisation.name_resolver.get("menubar_file_save_as"),
            command=self.save_file_as)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=localisation.name_resolver.get("menubar_file_exit"), command=self.__on_closing)

        # MENU: Analiza (Zmodyfikowane)
        self.menu_analysis = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_analysis") or "Analiza",
                             menu=self.menu_analysis)
        self.menu_analysis.add_command(
            label="Analiza dla całego pliku",
            state=tk.DISABLED,
            command=None
            #command=self.__perform_full_file_analysis
        )
        self.menu_analysis.add_command(
            label=localisation.name_resolver.get("menubar_analysis_parameters"),
            state=tk.DISABLED,
            command=self.__open_parameters_window
        )

        # MENU: Opcje (Zupełnie nowe)
        self.menu_options = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Opcje", menu=self.menu_options)
        self.menu_options.add_checkbutton(
            label="Tryb Developera",
            variable=self.developer_mode_var,
            command=self.__on_developer_mode_toggled
        )

        # MENU: Pomoc
        self.menu_help = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_help"), menu=self.menu_help)
        self.menu_help.add_command(label="Instrukcja obsługi", command=self.__show_help_window)

        self.master.config(menu=menu_bar)

    def open_file_dialog(self, filepath: str | None = None) -> None:
        try:
            if filepath:
                self.file_manager.open_file(filepath=filepath)
            else:
                self.file_manager.open_file_system_gui()

            if self.file_manager.opened() and self.file_manager.signals:
                fs = self.file_manager.sampling_frequency
                self.preproc_manager = PreprocManager(sampling_frequency=fs)

                self.frame_buttons.preproc_manager = self.preproc_manager

                self.display_manager.reset_to_defaults(self.file_manager.get_available_leads())

                self.display_manager.show_frequency_analysis = True

                self.navigation_manager.reset_for_new_file(fs=fs, total_samples=self.file_manager.get_total_samples())
                self.analysis_manager.reset_to_defaults()

                # Odblokowanie przycisków analizy
                self.menu_analysis.entryconfig(0, state=tk.NORMAL)
                self.menu_analysis.entryconfig(1, state=tk.NORMAL)

                self.chosen_annotation = -1
                self.update_header_info()
                self.update()

        except Exception as error_obj:
            traceback.print_exc()
            messagebox.showerror(
                title=localisation.name_resolver.get("messagebox_error"),
                message=f"{localisation.name_resolver.get('messagebox_could_not_read_file')}:\n{str(object=error_obj)}"
            )

    def save_file(self) -> None:
        try:
            self.file_manager.save_file(self.file_manager.filepath)
        except Exception as error_obj:
            messagebox.showerror(
                title=localisation.name_resolver.get("messagebox_error"),
                message=f"{localisation.name_resolver.get('messagebox_could_not_save_file')}:\n{str(object=error_obj)}"
            )

    def save_file_as(self) -> None:
        try:
            self.file_manager.save_file_system_gui()
        except Exception as error_obj:
            messagebox.showerror(
                title=localisation.name_resolver.get("messagebox_error"),
                message=f"{localisation.name_resolver.get('messagebox_could_not_save_file')}:\n{str(object=error_obj)}"
            )

    def update(self):
        from_sample = int(round(self.navigation_manager.current_sample))
        window_samples = int(round(self.navigation_manager.window_size_sec * self.navigation_manager.current_fs))
        to_sample = int(min(from_sample + window_samples, self.navigation_manager.total_samples))

        time_axis = self.file_manager.get_time_axis(from_sample=from_sample, to_sample=to_sample)
        fs = self.file_manager.sampling_frequency

        signals_to_draw = {}
        for lead in self.display_manager.displayed_leads:
            signals_to_draw[lead] = self.file_manager.get_signal(
                channel=lead,
                from_sample=from_sample,
                to_sample=to_sample
            )

        fft_dict_to_draw = {}
        is_analysis_active = self.display_manager.show_frequency_analysis
        has_valid_times = self.analysis_manager.analysis_start >= 0 and self.analysis_manager.analysis_end >= 0

        if is_analysis_active and has_valid_times and self.preproc_manager is not None:
            start_idx = int(round(self.analysis_manager.analysis_start * fs))
            end_idx = int(round(self.analysis_manager.analysis_end * fs))

            for lead in self.display_manager.displayed_leads:
                full_signal = self.file_manager.get_signal(channel=lead)
                try:
                    fft_result = self.preproc_manager.get_ft_portion(
                        data=full_signal,
                        start_idx=start_idx,
                        end_idx=end_idx
                    )

                    if len(fft_result) == 4:
                        freqs, mags, actual_start_idx, actual_end_idx = fft_result
                        fft_dict_to_draw[lead] = (freqs, mags, actual_start_idx / fs, actual_end_idx / fs)
                    else:
                        fft_dict_to_draw[lead] = fft_result

                except Exception as e:
                    print(f"Ostrzeżenie FFT dla {lead}: {e}")
                    fft_dict_to_draw[lead] = None

        annotations_in_window = self.file_manager.get_annotations(from_sample=from_sample, to_sample=to_sample)

        self.frame_annotations.update_data(
            all_annotations=self.file_manager.annotations,
            window_annotations=annotations_in_window,
            sample_rate=fs
        )

        current_filter = self.frame_annotations.filter_var.get()
        filter_all = self.frame_annotations.atList.filter_all_text
        annotation_times_to_draw = []

        if fs > 0:
            for ann in annotations_in_window:
                if current_filter in ("", filter_all) or ann.annotation_type.to_string() == current_filter:
                    annotation_times_to_draw.append(ann.sample_index / fs)

        chosen_time_sec = self.chosen_annotation / fs if (self.chosen_annotation != -1 and fs > 0) else None

        self.frame_ecg.update_charts(
            time_axis=time_axis,
            signals_dict=signals_to_draw,
            fft_data_dict=fft_dict_to_draw,
            overlap_sec=self.navigation_manager.overlap_sec,
            is_first=self.navigation_manager.is_first_window(),
            is_last=self.navigation_manager.is_last_window(),
            annotation_times=annotation_times_to_draw,
            highlighted_time=chosen_time_sec
        )

        current_time_str = self.navigation_manager.get_current_time_string()
        self.frame_buttons.update_time_display(current_time_str)

    def jump_annotation(self, direction: int):
        all_anns = self.file_manager.annotations
        fs = self.file_manager.sampling_frequency

        if fs <= 0 or not all_anns:
            return

        current_filter = self.frame_annotations.filter_var.get()
        filter_all = self.frame_annotations.atList.filter_all_text

        filtered_anns = []
        for ann in all_anns:
            if current_filter in ("", filter_all) or ann.annotation_type.to_string() == current_filter:
                filtered_anns.append(ann)

        if not filtered_anns:
            return

        current_idx = -1
        if self.chosen_annotation != -1:
            for i, ann in enumerate(filtered_anns):
                if ann.sample_index == self.chosen_annotation:
                    current_idx = i
                    break

        if current_idx == -1:
            current_start_sample = self.navigation_manager.current_sample
            for i, ann in enumerate(filtered_anns):
                if ann.sample_index >= current_start_sample:
                    if direction == 1:
                        target_idx = i
                    else:
                        target_idx = max(0, i - 1)
                    break
            else:
                target_idx = len(filtered_anns) - 1
        else:
            target_idx = current_idx + direction

        if target_idx < 0:
            target_idx = 0
        elif target_idx >= len(filtered_anns):
            target_idx = len(filtered_anns) - 1

        target_ann = filtered_anns[target_idx]
        self.chosen_annotation = target_ann.sample_index

        self.navigation_manager.center_on_sample(target_ann.sample_index)
        self.update()

    def update_header_info(self):
        if self.file_manager.opened():
            print(self.file_manager.filepath)
            filename = os.path.basename(self.file_manager.filepath)
            fs = self.file_manager.sampling_frequency
            start_date = self.file_manager.base_datetime.strftime(
                "%Y-%m-%d %H:%M:%S") if self.file_manager.base_datetime else "Brak daty"
            total_sec = self.file_manager.get_duration_seconds()

            self.label_file_info.config(text=f"Plik: {filename}")
            self.label_fs_info.config(text=f"Fs: {fs} Hz")
            self.label_duration_info.config(text=f"Czas trwania: {total_sec:.2f} [s]")

            patient_name = self.file_manager.comments.get("patient", "Nieznany")
            if patient_name == "Nieznany" and self.file_manager.comments:
                patient_name = next(iter(self.file_manager.comments.values()), "Nieznany")
            self.label_patient_name.config(text=f"Pacjent: {patient_name}")

            date_str = self.file_manager.base_datetime.strftime(
                "%d.%m.%Y %H:%M") if self.file_manager.base_datetime else "Brak daty"
            self.label_date_info.config(text=f"Data: {date_str}")

    def __on_closing(self):
        self.master.quit()
        self.master.destroy()

    def __open_parameters_window(self):
        params_window = ParametersWindow(
            master=self.master,
            file_manager=self.file_manager,
            display_manager=self.display_manager,
            analysis_manager=self.analysis_manager,
            navigation_manager=self.navigation_manager)
        params_window.grab_set()
        self.master.wait_window(params_window)

        window_samples = int(round(self.navigation_manager.window_size_sec * self.navigation_manager.current_fs))
        if self.navigation_manager.current_sample + window_samples > self.navigation_manager.total_samples:
            self.navigation_manager.current_sample = max(0, self.navigation_manager.total_samples - window_samples)
        self.update()

    def __perform_full_file_analysis(self):
        return

    def __on_developer_mode_toggled(self):
        # Ta metoda odpali się, kiedy użyjesz przełącznika Tryb Developera
        is_dev = self.developer_mode_var.get()
        if is_dev:
            print("Tryb Developera włączony. Możesz tu dodać odblokowanie ukrytych przycisków!")
        else:
            print("Tryb Developera wyłączony.")

    def on_annotation_clicked(self, chosen_index: int):
        self.chosen_annotation = chosen_index
        self.update()

    def __show_help_window(self):
        if hasattr(self, 'help_window') and self.help_window.winfo_exists():
            self.help_window.lift()
        else:
            self.help_window = HelpWindow(self.master)