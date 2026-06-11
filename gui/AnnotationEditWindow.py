import tkinter as tk
from tkinter import ttk

import localisation
from file_manager import Annotation, EAnnotationType


class AnnotationEditWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, annotation: Annotation, on_save_callback=None):
        super().__init__(master)

        self.annotation = annotation
        self.on_save_callback = on_save_callback

        self.title("Edycja adnotacji")

        window_width = 400
        window_height = 350
        center_x = self.winfo_screenwidth() // 2 - window_width // 2
        center_y = self.winfo_screenheight() // 2 - window_height // 2
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        self.transient(master)
        self.grab_set()

        self.__create_widgets()
        self.__load_data()

    def __create_widgets(self):
        padding = {'padx': 15, 'pady': 5}

        tk.Label(self, text="Typ adnotacji:", font=("Arial", 10, "bold")).pack(anchor=tk.W, **padding)
        self.type_var = tk.StringVar()
        self.type_cb = ttk.Combobox(self, textvariable=self.type_var, state="readonly")

        self.type_cb['values'] = [e.name for e in EAnnotationType]
        self.type_cb.pack(fill=tk.X, **padding)
        self.type_cb.bind("<<ComboboxSelected>>", self.__on_type_changed)

        tk.Label(self, text="Symbol / Etykieta własna:", font=("Arial", 10, "bold")).pack(anchor=tk.W, **padding)
        self.label_var = tk.StringVar()
        self.label_entry = tk.Entry(self, textvariable=self.label_var)
        self.label_entry.pack(fill=tk.X, **padding)

        tk.Label(self, text="Uwagi:", font=("Arial", 10, "bold")).pack(anchor=tk.W, **padding)
        self.note_text = tk.Text(self, height=6)
        self.note_text.pack(fill=tk.BOTH, expand=True, **padding)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=15, padx=15)

        save_btn = tk.Button(btn_frame, text="Zapisz", cursor="hand2", bg="lightgreen", command=self.__save)
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_btn = tk.Button(btn_frame, text="Anuluj", cursor="hand2", bg="lightcoral", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT)

    def __load_data(self):
        """Wczytuje dane z przekazanego obiektu adnotacji do widoku."""
        self.type_var.set(self.annotation.annotation_type.name)

        if self.annotation.custom_label:
            self.label_var.set(self.annotation.custom_label)

        if self.annotation.auxiliary_note:
            self.note_text.insert("1.0", self.annotation.auxiliary_note)

        self.__on_type_changed()

    def __on_type_changed(self, event=None):
        """Logika UI: blokuje wpisywanie własnej etykiety, jeśli typ jest inny niż CUSTOM."""
        selected_type = self.type_var.get()
        if selected_type == EAnnotationType.CUSTOM.name:
            self.label_entry.config(state=tk.NORMAL)
        else:
            self.label_entry.delete(0, tk.END)
            self.label_entry.config(state=tk.DISABLED)

    def __save(self):
        """Zapisuje zmienione wartości z powrotem do obiektu i odświeża główny widok."""
        selected_type_name = self.type_var.get()
        new_label = self.label_var.get().strip()
        new_note = self.note_text.get("1.0", tk.END).strip()

        self.annotation.annotation_type = EAnnotationType[selected_type_name]

        if self.annotation.annotation_type == EAnnotationType.CUSTOM:
            self.annotation.custom_label = new_label if new_label else None
        else:
            self.annotation.custom_label = None

        self.annotation.auxiliary_note = new_note

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()