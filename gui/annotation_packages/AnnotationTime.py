import tkinter as tk
from tkinter import ttk

import file_manager
import localisation

class AnnotationTime(tk.Frame):
    def __init__(self, master: tk.Widget, **kwargs: dict) -> None:
        super().__init__(master, **kwargs)

        self.current_annotations: list[file_manager.Annotation] = []
        self.current_sample_rate: float = 0.0

        self.filter_all_text = (localisation.name_resolver.get("frame_annotationframe_table_time_filter_all"))

        columns: tuple[str, str, str, str] = ("time", "type", "type_verbose", "note")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading(column="time", text=localisation.name_resolver.get("frame_annotationframe_table_time_label"))
        self.tree.heading(column="type", text=localisation.name_resolver.get("frame_annotationframe_table_type_label"))
        self.tree.heading(column="type_verbose",
                          text=localisation.name_resolver.get("frame_annotationframe_table_type_verbose_label"))
        self.tree.heading(column="note", text=localisation.name_resolver.get("frame_annotationframe_table_note_label"))

        self.tree.column(column="time", width=80, anchor=tk.CENTER)
        self.tree.column(column="type", width=40, anchor=tk.CENTER)
        self.tree.column(column="type_verbose", width=250, anchor=tk.W)
        self.tree.column(column="note", width=100, anchor=tk.W)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def set_data(self, annotations: list[file_manager.Annotation], sample_rate: float) -> None:
        self.current_annotations = annotations
        self.current_sample_rate = sample_rate

    def apply_filter(self, selected_type: str) -> None:
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)

        fs_valid = self.current_sample_rate > 0

        for annotation_obj in self.current_annotations:
            ann_type_str = annotation_obj.annotation_type.to_string()

            if selected_type == self.filter_all_text or selected_type == ann_type_str:
                time_in_seconds: float = annotation_obj.sample_index / self.current_sample_rate if fs_valid else 0.0

                self.tree.insert(
                    parent="",
                    index=tk.END,
                    values=(
                        f"{time_in_seconds:.3f}",
                        ann_type_str,
                        annotation_obj.get_display_name(name_resolver=localisation.name_resolver),
                        annotation_obj.auxiliary_note
                    )
                )