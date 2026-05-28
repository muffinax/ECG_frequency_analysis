import traceback
import tkinter as tk
from tkinter import messagebox

import localisation
from file_manager import Annotation, EAnnotationOrigin, EAnnotationType


class AIController:
    def __init__(self, main_controller):
        self.main_controller = main_controller

        # Local references for easier access
        self.file_manager = main_controller.file_manager
        self.display_manager = main_controller.display_manager

    def cmd_run_ai_analysis(self):
        """
        Main method to run AI analysis on the currently loaded signal.
        """
        preproc_manager = self.main_controller.preproc_manager

        if not self.file_manager.opened() or preproc_manager is None:
            messagebox.showwarning(localisation.name_resolver.get("messagebox_error"), "Najpierw wczytaj plik!")
            return

        filename = self.file_manager.filepath or "Nieznany"
        loading_window = self._create_loading_window()

        try:
            all_ml_data = self._extract_ml_data(preproc_manager, filename)

            if not all_ml_data:
                loading_window.destroy()
                messagebox.showinfo("Analiza AI", "Brak okien STFT do analizy.")
                return

            from ai_api.ai_handler import use_model
            predictions = use_model(all_ml_data)

            added_count = self._generate_annotations(all_ml_data, predictions)

            self.main_controller.refresh_view()
            loading_window.destroy()
            messagebox.showinfo("Analiza zakończona", f"Wygenerowano adnotacji AI: {added_count}")

        except Exception as e:
            loading_window.destroy()
            traceback.print_exc()
            error_title = localisation.name_resolver.get("frame_annotationframe_table_label")
            messagebox.showerror("Błąd AI", f"{error_title}: {str(e)}")

    def _create_loading_window(self) -> tk.Toplevel:
        """
        Creates and displays a modal loading window
        to indicate that AI analysis is in progress.
        """
        master_window = self.main_controller.view.master
        loading_window = tk.Toplevel(master_window)
        loading_window.title("Trwa analiza...")
        loading_window.geometry("300x100")
        loading_window.transient(master_window)
        loading_window.grab_set()
        loading_window.resizable(False, False)
        loading_window.update_idletasks()

        x = master_window.winfo_x() + (master_window.winfo_width() // 2) - 150
        y = master_window.winfo_y() + (master_window.winfo_height() // 2) - 50
        loading_window.geometry(f"+{x}+{y}")

        tk.Label(loading_window, text="Trwa analiza sygnału przez AI...\nProszę czekać.",
                 font=("Arial", 11)).pack(expand=True, fill=tk.BOTH)
        loading_window.update()

        return loading_window

    def _extract_ml_data(self, preproc_manager, filename: str) -> list:
        """
        Extracts machine learning data (STFT windows) for all displayed leads.
        """
        all_ml_data = []
        for lead in self.display_manager.displayed_leads:
            signal = self.file_manager.get_signal(channel=lead)
            ml_data_list = preproc_manager.get_stft_whole(signal, filename, lead)

            for ml_data in ml_data_list:
                self.file_manager.machine_learning_data.append(ml_data)
                all_ml_data.append(ml_data)

        return all_ml_data

    def _generate_annotations(self, all_ml_data: list, predictions) -> int:
        """
        Generates annotations based on AI predictions and adds them to the file manager.
        Returns the count of generated annotations.
        """
        pred_bin = (predictions > 0.2).astype(int)
        reverse_label_map = {0: "+", 1: "/", 2: "L", 3: "R", 4: "V", 5: "~"}
        added_count = 0

        for i, ml_data in enumerate(all_ml_data):
            active_classes = [reverse_label_map[idx] for idx, val in enumerate(pred_bin[i]) if val == 1]

            if not active_classes:
                continue

            new_ann = Annotation(
                sample_index=int(ml_data.signal_sample_index_start * self.file_manager.sampling_frequency),
                annotation_duration=int(ml_data.signal_duration * self.file_manager.sampling_frequency),
                annotation_origin=EAnnotationOrigin.ANALYSIS,
                annotation_type=EAnnotationType.CUSTOM,
                auxiliary_note="Zidentyfikowano przez AI",
                channel=getattr(ml_data, 'signal_name', None),
                custom_label=",".join(active_classes)
            )

            self.file_manager.add_annotation(new_ann)
            added_count += 1

        return added_count