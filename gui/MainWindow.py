import os
import sys
import tkinter as tk
from tkinter import messagebox

from gui.AnnotationFrame import AnnotationFrame
from gui.display_data.DisplayManager import DisplayManager
from gui.ECGFrame import ECGFrame
from gui.SettingsFrame import SettingsFrame
from gui.display_data.NavigationManager import NavigationManager
from gui.parameters_window.ParametersWindow import ParametersWindow

from file_manager import FileManager
import localisation
from localisation import name_resolver


class MainWindow:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master

        self.file_manager = FileManager()
        self.display_manager = DisplayManager()
        self.navigation_manager = NavigationManager()

        if sys.platform == 'win32':
            #Windows
            self.master.state('zoomed')
        elif sys.platform.startswith('linux'):
            #Linux
            self.master.attributes('-zoomed', True)
        else:
            #macOS
            self.master.attributes('-fullscreen', True)
            pass

        self.master.title(localisation.name_resolver.get("main_title"))
        self.__create_menu()

        self.frame_annotations = AnnotationFrame(master=self.master, width=600)
        self.frame_annotations.pack_propagate(False)
        self.frame_annotations.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_buttons = SettingsFrame(
            master=self.master,
            navigation_manager=self.navigation_manager,
            on_update_callback=self.update,
            height=80
        )
        self.frame_buttons.pack_propagate(False)
        self.frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        #HEADER
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

        #ECG CHARTS
        self.frame_ecg = ECGFrame(master=self.master, display_manager=self.display_manager)
        self.frame_ecg.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.master.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __create_menu(self) -> None:
        menu_bar = tk.Menu(master=self.master)

        self.menu_file = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_file"), menu=self.menu_file)

        self.menu_file.add_command(
            label=localisation.name_resolver.get("menubar_file_open"),
            command=self.open_file_dialog)
        self.menu_file.add_command(
            label=localisation.name_resolver.get("menubar_file_save"),
            state=tk.DISABLED,
            command=None)
        self.menu_file.add_command(
            label=localisation.name_resolver.get("menubar_file_save_as"),
            state=tk.DISABLED,
            command=None)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=localisation.name_resolver.get("menubar_file_exit"), command=self.__on_closing)

        self.menu_analysis = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_analysis"), menu=self.menu_analysis)
        self.menu_analysis.add_command(
            label=localisation.name_resolver.get("menubar_analysis_perform_analysis"),
            state=tk.DISABLED,
            command=None)
        self.menu_analysis.add_command(
            label=localisation.name_resolver.get("menubar_analysis_parameters"),
            state=tk.DISABLED,
            command=self.__open_parameters_window)

        self.menu_help = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_help"), menu=self.menu_help)

        self.menu_help.add_command(
            label=localisation.name_resolver.get("menubar_help_keys"),
            command=None)

        self.master.config(menu=menu_bar)

    def open_file_dialog(self) -> None:
        try:
            self.file_manager.open_file_system_gui()

            if self.file_manager.opened() and self.file_manager.signals:
                self.display_manager.reset_to_defaults(self.file_manager.get_available_leads())
                self.navigation_manager.reset_for_new_file(fs=self.file_manager.sampling_frequency,total_samples=self.file_manager.get_total_samples())
                self.update_header_info()
                self.update()
                self.menu_analysis.entryconfig(0, state=tk.NORMAL)
                self.menu_analysis.entryconfig(1, state=tk.NORMAL)

        except Exception as error_obj:
            messagebox.showerror(
                title=localisation.name_resolver.get("messagebox_error"),
                message=f"{localisation.name_resolver.get("messagebox_could_not_read_file")}:\n{str(object=error_obj)}"
            )

    def update(self):
        current_sample_float = self.navigation_manager.current_sample
        from_sample = int(round(current_sample_float))

        window_samples = int(round(self.navigation_manager.window_size_sec * self.navigation_manager.current_fs))

        to_sample = min(from_sample + window_samples, self.navigation_manager.total_samples)

        time_axis = self.file_manager.get_time_axis(from_sample=from_sample, to_sample=to_sample)

        signals_to_draw = {}
        for lead in self.display_manager.displayed_leads:
            signals_to_draw[lead] = self.file_manager.get_signal(
                channel=lead,
                from_sample=from_sample,
                to_sample=to_sample
            )

        self.frame_ecg.update_charts(
            time_axis=time_axis,
            signals_dict=signals_to_draw,
            overlap_sec=self.navigation_manager.overlap_sec,
            is_first=self.navigation_manager.is_first_window(),
            is_last=self.navigation_manager.is_last_window())

        current_time_str = self.navigation_manager.get_current_time_string()
        self.frame_buttons.update_time_display(current_time_str)

        annotations_in_window = self.file_manager.get_annotations(from_sample=from_sample, to_sample=to_sample)
        fs = self.file_manager.sampling_frequency
        self.frame_annotations.update_annotations(
            annotations=annotations_in_window,
            sample_rate=fs
        )

    def update_header_info(self):
        if self.file_manager.opened():
            filename = os.path.basename(self.file_manager.filepath)
            fs = self.file_manager.sampling_frequency
            start_date = self.file_manager.base_datetime.strftime(
                "%Y-%m-%d %H:%M:%S") if self.file_manager.base_datetime else "Brak daty"

            total_sec = self.file_manager.get_duration_seconds()
            # hours = int(total_sec // 3600)
            # minutes = int((total_sec % 3600) // 60)
            # seconds = int(total_sec % 60)
            # duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            self.label_file_info.config(text=f"Plik: {filename}")
            self.label_fs_info.config(text=f"Fs: {fs} Hz")
            self.label_duration_info.config(text=f"Czas trwania: {total_sec:.2f} [s]")

            patient_name = self.file_manager.comments.get("patient", "Nieznany")
            if patient_name == "Nieznany" and self.file_manager.comments:
                patient_name = next(iter(self.file_manager.comments.values()), "Nieznany")
            self.label_patient_name.config(text=f"Pacjent: {patient_name}")

            self.label_date_info.config(text=f"Data: {start_date}")
            if self.file_manager.base_datetime:
                date_str = self.file_manager.base_datetime.strftime("%d.%m.%Y %H:%M")
            else:
                date_str = "Brak daty"
            self.label_date_info.config(text=f"Data: {date_str}")

    def __on_closing(self):
        self.master.quit()  # Stops mainloop
        self.master.destroy()  # Destroys widgets

    def __open_parameters_window(self):
        params_window = ParametersWindow(
            master=self.master,
            display_manager=self.display_manager)
        params_window.grab_set()
        self.master.wait_window(params_window)
        self.update()