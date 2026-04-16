import tkinter as tk

import localisation
from gui.display_data.DisplayManager import DisplayManager


class LeadsListFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager, **kwargs):
        super().__init__(master, **kwargs)

        self.display_manager = display_manager
        self.lead_checkbuttons = []

        lbl_leads = tk.Label(self, text=localisation.name_resolver.get("parameters_leads_label"), font=("Arial", 14, "bold"))
        lbl_leads.pack(pady=(10, 5), anchor="w", fill="x")

        grid_frame = tk.Frame(self)
        grid_frame.pack(padx=10, fill="x")

        max_columns = 4

        for index, lead in enumerate(self.display_manager.available_leads):
            var = tk.BooleanVar()

            if lead in self.display_manager.displayed_leads:
                var.set(True)
            else:
                var.set(False)

            chk = tk.Checkbutton(grid_frame, text=lead, variable=var, command=self._update_states)

            row = index // max_columns
            col = index % max_columns

            chk.grid(row=row, column=col, sticky="w", padx=10, pady=2)

            self.lead_checkbuttons.append({"lead": lead, "var": var, "widget": chk})

        self._update_states()

    def _update_states(self):
        checked_items = [item for item in self.lead_checkbuttons if item["var"].get()]

        if len(checked_items) == 1:
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