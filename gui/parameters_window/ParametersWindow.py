import tkinter as tk

import localisation
from file_manager import FileManager
from gui.display_data.AnalysisManager import AnalysisManager
from gui.display_data.DisplayManager import DisplayManager
from gui.parameters_window.DetailsFrame import DetailsFrame
from gui.parameters_window.LeadsListFrame import LeadsListFrame


class ParametersWindow(tk.Toplevel):
    def __init__(self, master, file_manager: FileManager, display_manager: DisplayManager, analysis_manager: AnalysisManager) -> None:
        super().__init__(master)

        self.file_manager = file_manager
        self.display_manager = display_manager
        self.analysis_manager = analysis_manager
        self.title(localisation.name_resolver.get("parameters_title"))

        window_width = 400
        window_height = 500

        center_x = self.winfo_screenwidth()//2 - window_width//2
        center_y = self.winfo_screenheight()//2 - window_height//2 - 50
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.frame_leads_list = LeadsListFrame(self, self.display_manager)
        self.frame_details = DetailsFrame(self, display_manager)

        save_button = tk.Button(
            self,
            text=localisation.name_resolver.get("parameters_save_button"),
            command=self.__save_and_close)

        self.frame_leads_list.pack()
        self.frame_details.pack()
        save_button.pack(pady=10)

    def __save_and_close(self):
        self.display_manager.displayed_leads = self.frame_leads_list.get_currently_checked()
        self.destroy()