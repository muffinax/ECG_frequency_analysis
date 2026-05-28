import tkinter as tk
from tkinter import ttk

import file_manager
import localisation
from gui.annotation_packages.AnnotationTime import AnnotationTime
from gui.annotation_packages.AnnotationFFT import AnnotationFFT


class AnnotationFrame(tk.Frame):
    def __init__(self, master: tk.Widget, on_filter_changed_callback=None, on_annotation_click_callback=None,
                 **kwargs: dict) -> None:
        super().__init__(master, **kwargs)
        self.on_filter_changed_callback = on_filter_changed_callback
        self.on_annotation_click_callback = on_annotation_click_callback
        self.configure(relief=tk.GROOVE, borderwidth=2)

        self.container_header = tk.Frame(self)

        self.title_label = tk.Label(self.container_header,
                                    text=localisation.name_resolver.get("frame_annotationframe_table_label"),
                                    font=("Arial", 14, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=(10, 0))

        self.label = tk.Label(self.container_header,
                              text=localisation.name_resolver.get("frame_annotationframe_table_filter"),
                              font=("Arial", 11, "bold"))

        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.container_header, textvariable=self.filter_var, state="readonly",
                                            width=15)

        self.filter_combobox.pack(side=tk.RIGHT, padx=(0, 10))
        self.label.pack(side=tk.RIGHT, padx=(0, 5))

        self.container_header.pack(fill=tk.X, pady=10)

        # TAB 1: TIME
        self.time_label = tk.Label(self, text=localisation.name_resolver.get("annotation_saved"), font=("Arial", 10, "bold"), fg="#444444")
        self.time_label.pack(side=tk.TOP, anchor=tk.W, padx=10)

        self.atList = AnnotationTime(self, on_click_callback=lambda idx: self._on_table_clicked(idx, "time"))
        self.atList.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=(5, 0), pady=(0, 5))

        # TAB 2: FFT
        self.fft_label = tk.Label(self, text=localisation.name_resolver.get("annotation_ai"), font=("Arial", 10, "bold"), fg="#444444")
        self.fft_label.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(10, 0))

        self.mlList = AnnotationFFT(self, on_click_callback=lambda idx: self._on_table_clicked(idx, "fft"))
        self.mlList.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=(5, 0), pady=(0, 5))

        self.filter_combobox.bind("<<ComboboxSelected>>", self._on_filter_changed)

        self._last_time_annotations_ref = None
        self._time_annotations = []

        self._last_ml_annotations_ref = None
        self._ml_annotations = []

    def _on_table_clicked(self, chosen_index: int, source: str):
        """Synchronized blue frame"""
        if source == "time":
            # When Time chosen, hide FFT
            self.mlList.chosen_annotation = -1
            for item in self.mlList.tree.selection():
                self.mlList.tree.selection_remove(item)
        else:
            # when FFT chosen, hide Time
            self.atList.chosen_annotation = -1
            for item in self.atList.tree.selection():
                self.atList.tree.selection_remove(item)

        if self.on_annotation_click_callback:
            self.on_annotation_click_callback(chosen_index)

    def update_data(self, time_annotations: list[file_manager.Annotation], ml_annotations: list[file_manager.Annotation],
                    window_ml_annotations: list[file_manager.Annotation], window_annotations: list[file_manager.Annotation],
                    sample_rate: float) -> None:

        self._time_annotations = time_annotations
        self._ml_annotations = ml_annotations
        self.atList.set_data(window_annotations, sample_rate)
        self.mlList.set_data(window_ml_annotations, sample_rate)

        # Ref values
        if not hasattr(self, '_last_ml_annotations_ref'):
            self._last_ml_annotations_ref = None
        if not hasattr(self, '_last_time_annotations_ref'):
            self._last_time_annotations_ref = None

        # Change filter value if annotation classification changed
        if (self._last_time_annotations_ref is not self._time_annotations) or \
                (self._last_ml_annotations_ref is not self._ml_annotations):

            self._last_time_annotations_ref = self._time_annotations
            self._last_ml_annotations_ref = self._ml_annotations

            unique_types = set()

            # Pobieranie typów ze zwykłych adnotacji czasowych
            for ann in self._time_annotations:
                unique_types.add(ann.annotation_type.to_string())

            # Pobieranie typów z adnotacji AI (teraz to zwykłe obiekty Annotation!)
            for ann in self._ml_annotations:
                unique_types.add(ann.annotation_type.to_string())

            # New List of filters added to combobox
            combobox_values = [self.atList.filter_all_text] + sorted(list(unique_types))
            self.filter_combobox["values"] = combobox_values

            if self.filter_var.get() not in combobox_values:
                self.filter_combobox.current(0)

        self.atList.apply_filter(self.filter_var.get())
        self.mlList.apply_filter(self.filter_var.get())

    def _on_filter_changed(self, event: tk.Event = None) -> None:
        selected_type = self.filter_var.get()

        # Sprawdzamy, czy cokolwiek jest zaznaczone (w którejkolwiek tabeli)
        chosen_idx = self.atList.chosen_annotation
        if chosen_idx == -1:
            chosen_idx = self.mlList.chosen_annotation

        if chosen_idx != -1:
            found_ann = next((a for a in self._time_annotations if a.sample_index == chosen_idx), None)

            if found_ann:
                current_type = found_ann.annotation_type.to_string()
                if selected_type != self.atList.filter_all_text and current_type != selected_type:

                    self.atList.chosen_annotation = -1
                    self.mlList.chosen_annotation = -1

                    if self.on_annotation_click_callback:
                        self.on_annotation_click_callback(-1)

        self.atList.apply_filter(selected_type)
        self.mlList.apply_filter(selected_type)

        if self.on_filter_changed_callback:
            self.on_filter_changed_callback()