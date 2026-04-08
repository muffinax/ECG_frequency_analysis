import tkinter as tk
from tkinter import messagebox

from gui.AnnotationFrame import AnnotationFrame
from gui.ECGFrame import ECGFrame
from gui.SettingsFrame import SettingsFrame

from file_manager import FileManager
import localisation


class MainWindow:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master

        self.file_manager = FileManager()

        self.master.state('zoomed')
        self.master.title("ECG frequency analysis")
        self.__create_menu()

        self.frame_annotations = AnnotationFrame(master=self.master, width=600)
        self.frame_annotations.pack_propagate(False)
        self.frame_annotations.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_buttons = SettingsFrame(master=self.master, height=80)
        self.frame_buttons.pack_propagate(False)
        self.frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        self.frame_ecg = ECGFrame(master=self.master)
        self.frame_ecg.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.master.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __create_menu(self) -> None:
        menu_bar = tk.Menu(master=self.master)

        menu_file = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_file"), menu=menu_file)

        menu_file.add_command(label=localisation.name_resolver.get("menubar_file_open"), command=self.open_file_dialog)

        menu_file.add_command(label=localisation.name_resolver.get("menubar_file_save"), command=None)
        menu_file.add_command(label=localisation.name_resolver.get("menubar_file_save_as"), command=None)
        menu_file.add_separator()
        menu_file.add_command(label=localisation.name_resolver.get("menubar_file_exit"), command=self.__on_closing)

        menu_analysis = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label=localisation.name_resolver.get("menubar_analysis"), menu=menu_analysis)
        menu_analysis.add_command(label=localisation.name_resolver.get("menubar_analysis_perform_analysis"), command=None)

        self.master.config(menu=menu_bar)

    def open_file_dialog(self) -> None:
        try:
            self.file_manager.open_file_system_gui()

            if self.file_manager.opened() and self.file_manager.signals:
                self.update()

        except Exception as error_obj:
            messagebox.showerror(
                title=localisation.name_resolver.get("messagebox_error"),
                message=f"{localisation.name_resolver.get("messagebox_could_not_read_file")}:\n{str(object=error_obj)}"
            )

    def update(self):
        first_available_lead: str = list(self.file_manager.signals.keys())[0]
        time_axis = self.file_manager.get_time_axis()
        amplitude = self.file_manager.get_signal(channel=first_available_lead)
        self.frame_ecg.update_chart(t=time_axis, a=amplitude)

        annotations_list = self.file_manager.get_annotations()
        fs = self.file_manager.sampling_frequency
        self.frame_annotations.update_annotations(
            annotations=annotations_list,
            sample_rate=fs
        )

        self.master.title(f"ECG frequency analysis - Lead: {first_available_lead}")

    def __on_closing(self):
        self.master.quit()  # Stops mainloop
        self.master.destroy()  # Destroys widgets