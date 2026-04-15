import tkinter as tk

from gui.display_data.DisplayManager import DisplayManager


class LeadsListFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager, **kwargs):
        super().__init__(master, **kwargs)

        self.display_manager = display_manager

        self.lead_checkbuttons=[]

        for lead in self.display_manager.available_leads:
            var = tk.BooleanVar()

            if lead in self.display_manager.displayed_leads:
                var.set(True)
            else:
                var.set(False)

            chk = tk.Checkbutton(self, text=lead, variable=var, command=self._update_states)
            chk.pack(anchor="w")
            self.lead_checkbuttons.append({"lead": lead, "var": var, "widget": chk})

        self._update_states()

    def _update_states(self):
        #How many checked
        checked_items = [item for item in self.lead_checkbuttons if item["var"].get()]

        if len(checked_items) == 1:
            #at least one must be checked
            for item in self.lead_checkbuttons:
                if item["var"].get():
                    item["widget"].config(state=tk.DISABLED)
                else:
                    item["widget"].config(state=tk.NORMAL)
        else:
            for item in self.lead_checkbuttons:
                item["widget"].config(state=tk.NORMAL)

    def get_currently_checked(self) -> list[str]:
        return [item["lead"] for item in self.lead_checkbuttons if item["var"].get()]