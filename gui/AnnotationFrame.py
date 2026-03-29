import tkinter as tk
from tkinter import ttk

import file_manager
import localisation


class AnnotationFrame(tk.Frame):
    def __init__(self, master: tk.Widget, **kwargs: dict) -> None:
        super().__init__(master, **kwargs)

        self.label = tk.Label(self, text=localisation.name_resolver.get("frame_annotationframe_table_label"), font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        columns: tuple[str, str, str, str] = ("time", "type", "type_verbose", "note")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading(column="time", text=localisation.name_resolver.get("frame_annotationframe_table_time_label"))
        self.tree.heading(column="type", text=localisation.name_resolver.get("frame_annotationframe_table_type_label"))
        self.tree.heading(column="type_verbose", text=localisation.name_resolver.get("frame_annotationframe_table_type_verbose_label"))
        self.tree.heading(column="note", text=localisation.name_resolver.get("frame_annotationframe_table_note_label"))

        self.tree.column(column="time", width=80, anchor=tk.CENTER)
        self.tree.column(column="type", width=40, anchor=tk.CENTER)
        self.tree.column(column="type_verbose", width=250, anchor=tk.W)
        self.tree.column(column="note", width=100, anchor=tk.W)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

    def update_annotations(self, annotations: list[file_manager.Annotation], sample_rate: float) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for annotation_obj in annotations:
            time_in_seconds: float = annotation_obj.sample_index / sample_rate if sample_rate > 0 else 0.0
            self.tree.insert(
                parent="",
                index=tk.END,
                values=(
                    f"{time_in_seconds:.3f}",
                    annotation_obj.annotation_type.to_string(),
                    annotation_obj.get_display_name(name_resolver=localisation.name_resolver),
                    annotation_obj.auxiliary_note
                )
            )

