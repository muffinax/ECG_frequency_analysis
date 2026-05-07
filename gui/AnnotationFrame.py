import tkinter as tk
from tkinter import ttk

import file_manager
import localisation
from gui.annotation_packages.AnnotationTime import AnnotationTime


class AnnotationFrame(tk.Frame):
    def __init__(self, master: tk.Widget, on_filter_changed_callback=None, on_annotation_click_callback=None, **kwargs: dict) -> None:
        super().__init__(master, **kwargs)
        self.on_filter_changed_callback = on_filter_changed_callback
        self.on_annotation_click_callback = on_annotation_click_callback
        self.configure(relief=tk.GROOVE, borderwidth=2)

        self.container_header = tk.Frame(self)

        self.title_label = tk.Label(self.container_header, text=localisation.name_resolver.get("frame_annotationframe_table_label"), font=("Arial", 14, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=(10, 0))

        self.label = tk.Label(self.container_header,
                              text=localisation.name_resolver.get("frame_annotationframe_table_filter"),
                              font=("Arial", 11, "bold"))

        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.container_header, textvariable=self.filter_var, state="readonly", width=15)

        self.filter_combobox.pack(side=tk.RIGHT, padx=(0, 10))
        self.label.pack(side=tk.RIGHT, padx=(0, 5))

        self.container_header.pack(fill=tk.X, pady=10)

        self.atList = AnnotationTime(self, on_click_callback=on_annotation_click_callback)
        self.atList.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", self._on_filter_changed)

        self._last_all_annotations_ref = None
        self._all_annotations = []

    def update_data(self, all_annotations: list[file_manager.Annotation],
                    window_annotations: list[file_manager.Annotation], sample_rate: float) -> None:

        self._all_annotations = all_annotations
        self.atList.set_data(window_annotations, sample_rate)

        if self._last_all_annotations_ref is not all_annotations:
            self._last_all_annotations_ref = all_annotations

            unique_types = sorted(list({ann.annotation_type.to_string() for ann in all_annotations}))
            combobox_values = [self.atList.filter_all_text] + unique_types
            self.filter_combobox["values"] = combobox_values

            if self.filter_var.get() not in combobox_values:
                self.filter_combobox.current(0)

        # Rysujemy na ekranie to, co jest aktualnie w oknie
        self.atList.apply_filter(self.filter_var.get())

    def _on_filter_changed(self, event: tk.Event = None) -> None:
        selected_type = self.filter_var.get()
        chosen_idx = self.atList.chosen_annotation

        if chosen_idx != -1:
            found_ann = next((a for a in self._all_annotations if a.sample_index == chosen_idx), None)

            if found_ann:
                current_type = found_ann.annotation_type.to_string()
                if selected_type != self.atList.filter_all_text and current_type != selected_type:
                    self.atList.chosen_annotation = -1
                    if self.on_annotation_click_callback:
                        self.on_annotation_click_callback(-1)

        self.atList.apply_filter(selected_type)

        if self.on_filter_changed_callback:
            self.on_filter_changed_callback()