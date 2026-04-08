import tkinter as tk

from file_manager import FileManager
from gui.display_data.DisplayManager import DisplayManager


class LeadsListFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager, file_manager: FileManager, **kwargs):
        super().__init__(master, **kwargs)

        self.display_manager = display_manager

        self.lead_checkbuttons=[]

        for lead in file_manager.get_available_leads():
            var = tk.BooleanVar()

            if lead in self.display_manager.displayed_leads:
                var.set(True)
            else:
                var.set(False)

            chk = tk.Checkbutton(self, text=lead, variable=var)
            chk.pack(anchor="w")
            self.lead_checkbuttons.append({"lead": lead, "var": var, "widget": chk})

    def get_currently_checked(self) -> list[str]:
        return [item["lead"] for item in self.lead_checkbuttons if item["var"].get()]