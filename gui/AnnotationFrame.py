import tkinter as tk
from tkinter import ttk

# We type-hint the list, but we don't need to strictly import the Annotation class
# here if we just rely on duck typing for the loop, but let's be safe and rigorous.
from file_manager import Annotation


class AnnotationFrame(tk.Frame):
    def __init__(self, master: tk.Widget, **kwargs: dict) -> None:
        super().__init__(master, **kwargs)

        self.label = tk.Label(self, text="Detected Annotations", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        # Create the Treeview (Table) for annotations
        columns: tuple[str, str, str] = ("time", "type", "note")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        # Define headings
        self.tree.heading(column="time", text="Time [s]")
        self.tree.heading(column="type", text="Type")
        self.tree.heading(column="note", text="Note")

        # Format columns
        self.tree.column(column="time", width=80, anchor=tk.CENTER)
        self.tree.column(column="type", width=50, anchor=tk.CENTER)
        self.tree.column(column="note", width=100, anchor=tk.W)

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

    def update_annotations(self, annotations: list[Annotation], sample_rate: float) -> None:
        # Clear existing data in the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new annotations
        for annotation_obj in annotations:
            # Convert sample index to seconds for easier reading
            time_in_seconds: float = annotation_obj.sample_index / sample_rate if sample_rate > 0 else 0.0

            self.tree.insert(
                parent="",
                index=tk.END,
                values=(
                    f"{time_in_seconds:.3f}",
                    annotation_obj.annotation_type.to_string(),
                    annotation_obj.auxiliary_note
                )
            )