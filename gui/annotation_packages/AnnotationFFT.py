import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

import localisation
from gui.AiAnnDTO import AiAnnDTO


class AnnotationFFT(tk.Frame):
    def __init__(self, master: tk.Widget, on_click_callback=None, **kwargs: dict) -> None:
        super().__init__(master, **kwargs)

        self.on_click_callback = on_click_callback
        self.chosen_annotation = -1

        self.current_annotations: list[AiAnnDTO] = []
        self.current_sample_rate: float = 0.0

        self.filter_all_text = (localisation.name_resolver.get("frame_annotationframe_table_time_filter_all"))

        # 5 column is simulating button add and delete
        columns: tuple[str, str, str, str, str] = ("time", "type", "type_verbose", "note", "action")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading(column="time", text=localisation.name_resolver.get("frame_annotationframe_table_time_label"))
        self.tree.heading(column="type", text=localisation.name_resolver.get("frame_annotationframe_table_type_label"))
        self.tree.heading(column="type_verbose",
                          text=localisation.name_resolver.get("frame_annotationframe_table_type_verbose_label"))
        self.tree.heading(column="note", text=localisation.name_resolver.get("frame_annotationframe_table_note_label"))
        self.tree.heading(column="action", text="Akcja")  # Nowy nagłówek

        self.tree.column(column="time", width=70, anchor=tk.CENTER)
        self.tree.column(column="type", width=40, anchor=tk.CENTER)
        self.tree.column(column="type_verbose", width=220, anchor=tk.W)
        self.tree.column(column="note", width=90, anchor=tk.W)
        self.tree.column(column="action", width=85, anchor=tk.CENTER)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self._on_tree_click)

        self.bold_underline_font = tkfont.Font(font="TkDefaultFont")
        self.bold_underline_font.configure(weight="bold", underline=True)
        self.tree.tag_configure("saved_true", font=self.bold_underline_font)

    def set_data(self, annotations: list[AiAnnDTO], sample_rate: float) -> None:
        self.current_annotations = annotations
        self.current_sample_rate = sample_rate

    def apply_filter(self, selected_type: str) -> None:
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)

        fs_valid = self.current_sample_rate > 0

        for dto in self.current_annotations:
            annotation_obj = dto.annotation
            ann_type_str = annotation_obj.annotation_type.to_string()

            if selected_type == self.filter_all_text or selected_type == ann_type_str:
                time_in_seconds: float = annotation_obj.sample_index / self.current_sample_rate if fs_valid else 0.0

                row_tags = ("saved_true",) if dto.is_saved else ()

                action_btn_text = "[ USUŃ ]" if dto.is_saved else "[ DODAJ ]"

                item_id = self.tree.insert(
                    parent="",
                    index=tk.END,
                    values=(
                        f"{time_in_seconds:.3f}",
                        ann_type_str,
                        annotation_obj.get_display_name(name_resolver=localisation.name_resolver),
                        annotation_obj.auxiliary_note,
                        action_btn_text  # Wrzucamy do tabeli
                    ),
                    tags=row_tags
                )

                if annotation_obj.sample_index == self.chosen_annotation:
                    self.tree.selection_set(item_id)
                    self.tree.see(item_id)

    def _on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)

        if not item_id:
            if self.chosen_annotation != -1:
                self.chosen_annotation = -1
                if self.on_click_callback:
                    self.on_click_callback(-1)
            return

        values = self.tree.item(item_id, 'values')
        if not values:
            return

        clicked_time_str = values[0]
        clicked_sample_index = -1
        fs_valid = self.current_sample_rate > 0

        if column_id == '#5' and fs_valid:
            for dto in self.current_annotations:
                annotation_obj = dto.annotation
                time_in_seconds = annotation_obj.sample_index / self.current_sample_rate
                if f"{time_in_seconds:.3f}" == clicked_time_str:

                    dto.is_saved = not dto.is_saved

                    annotation_obj.is_saved = dto.is_saved

                    new_action_btn_text = "[ USUŃ ]" if dto.is_saved else "[ DODAJ ]"
                    new_values = (values[0], values[1], values[2], values[3], new_action_btn_text)
                    new_tags = ("saved_true",) if dto.is_saved else ()

                    self.tree.item(item_id, values=new_values, tags=new_tags)
                    return

        #Choosing
        if fs_valid:
            for dto in self.current_annotations:
                annotation_obj = dto.annotation
                time_in_seconds = annotation_obj.sample_index / self.current_sample_rate
                if f"{time_in_seconds:.3f}" == clicked_time_str:
                    clicked_sample_index = annotation_obj.sample_index
                    break

        if clicked_sample_index == -1:
            return

        if self.chosen_annotation == clicked_sample_index:
            self.chosen_annotation = -1
            self.tree.selection_remove(item_id)
        else:
            self.chosen_annotation = clicked_sample_index

        if self.on_click_callback:
            self.on_click_callback(self.chosen_annotation)