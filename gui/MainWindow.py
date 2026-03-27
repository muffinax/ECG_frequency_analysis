import tkinter as tk
from tkinter import messagebox

from gui.AnnotationFrame import AnnotationFrame
from gui.ECGFrame import ECGFrame
from gui.SettingsFrame import SettingsFrame

from file_manager import FileManager, ELeadType


class MainWindow:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master

        # Initialize the file manager here so the whole app can access it
        self.file_manager = FileManager()

        self.master.state('zoomed')
        self.master.title("ECG frequency analysis")
        self.__create_menu()

        self.frame_annotations = AnnotationFrame(master=self.master, width=300)
        self.frame_annotations.pack_propagate(False)
        self.frame_annotations.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_buttons = SettingsFrame(master=self.master, height=80)
        self.frame_buttons.pack_propagate(False)
        self.frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        self.frame_ecg = ECGFrame(master=self.master)
        self.frame_ecg.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def __create_menu(self) -> None:
        menu_bar = tk.Menu(master=self.master)

        menu_file = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label='File', menu=menu_file)

        # HOOKED UP HERE: command=self.open_file_dialog
        menu_file.add_command(label='Open..', command=self.open_file_dialog)

        menu_file.add_command(label='Save', command=None)
        menu_file.add_command(label='Save as...', command=None)
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.master.destroy)

        menu_analysis = tk.Menu(master=menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Analysis', menu=menu_analysis)
        menu_analysis.add_command(label='perform an ECG analysis', command=None)

        self.master.config(menu=menu_bar)

    def open_file_dialog(self) -> None:
        try:
            self.file_manager.open_file_system_gui()

            if self.file_manager.opened() and self.file_manager.signals:
                # 1. Update ECG Chart
                first_available_lead: ELeadType = list(self.file_manager.signals.keys())[0]
                time_axis = self.file_manager.get_time_axis()
                amplitude = self.file_manager.get_signal(channel=first_available_lead)
                self.frame_ecg.update_chart(t=time_axis, a=amplitude)

                # 2. Update Annotations Table
                annotations_list = self.file_manager.get_annotations()
                fs = self.file_manager.sampling_frequency
                self.frame_annotations.update_annotations(
                    annotations=annotations_list,
                    sample_rate=fs
                )

                # 3. Update Window Title
                self.master.title(f"ECG frequency analysis - Lead: {first_available_lead.to_string()}")

        except Exception as error_obj:
            messagebox.showerror(title="Error", message=f"Could not load file:\n{str(object=error_obj)}")