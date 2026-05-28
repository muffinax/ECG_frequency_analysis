import traceback
from tkinter import messagebox
import localisation

from file_manager import EAnnotationOrigin


class NavigationController:
    def __init__(self, main_controller):
        self.main_controller = main_controller

        # Local references for easier access
        self.file_manager = main_controller.file_manager
        self.display_manager = main_controller.display_manager
        self.navigation_manager = main_controller.navigation_manager
        self.analysis_manager = main_controller.analysis_manager


    def cmd_jump_annotation(self, direction: int, current_filter: str, filter_all_text: str, current_chosen_sample: int):
        """
        Navigating to next/previous annotation based on current filter and chosen sample
        """
        all_anns = self.file_manager.annotations
        fs = self.file_manager.sampling_frequency

        if fs <= 0 or not all_anns:
            return

        # Get filtered list
        filtered_anns = self._get_filtered_annotations(all_anns, current_chosen_sample, current_filter, filter_all_text)
        if not filtered_anns:
            return


        target_ann = self._find_target_annotation(filtered_anns, current_chosen_sample, direction)

        self.navigation_manager.center_on_sample(target_ann.sample_index)

        if self.main_controller.view:
            self.main_controller.view.chosen_annotation = target_ann.sample_index
            self.cmd_annotation_clicked(target_ann.sample_index)

    def cmd_annotation_clicked(self, chosen_index: int):
        """
        Handling click on annotation in table
        - showing frequency analysis if it's AI annotation with duration
        """
        fs = self.file_manager.sampling_frequency

        target_ann = next((ann for ann in self.file_manager.annotations if ann.sample_index == chosen_index), None)

        is_ai = target_ann and getattr(target_ann, 'annotation_origin', None) == EAnnotationOrigin.ANALYSIS
        duration = getattr(target_ann, 'annotation_duration', 0) if is_ai else 0

        if is_ai and duration > 0 and fs > 0:
            start_time = target_ann.sample_index / fs
            self.analysis_manager.analysis_start = start_time
            self.analysis_manager.analysis_end = start_time + (duration / fs)
            self.display_manager.show_frequency_analysis = True
            self.analysis_manager.fft_time_mode = self.analysis_manager.fft_time_mode.CUSTOM_TIME
        else:
            #Clearing analysis
            self.analysis_manager.analysis_start = -1.0
            self.analysis_manager.analysis_end = -1.0

        self.main_controller.refresh_view()

    def cmd_next_window(self):
        """
        Showing next window of signal
        (skipping by window size defined in settings)
        """
        self.navigation_manager.next_window()
        self.main_controller.refresh_view()

    def cmd_prev_window(self):
        """
        Showing previous window of signal
        (skipping by window size defined in settings)
        """
        self.navigation_manager.previous_window()
        self.main_controller.refresh_view()

    def cmd_jump_to_start(self):
        """
        Showing first window of signal
        (jumping to the start of signal)
        """
        self.navigation_manager.jump_to_start()
        self.main_controller.refresh_view()

    def cmd_jump_to_end(self):
        """
        Showing last window of signal
        (jumping to the end of signal)
        """
        self.navigation_manager.jump_to_end()
        self.main_controller.refresh_view()

    def cmd_jump_to_time(self, time_str: str):
        """
        Showing window of signal corresponding to time defined in time_str
        """
        try:
            self.navigation_manager.jump_to_time_string(time_str)
            self.main_controller.refresh_view()
        except ValueError:
            messagebox.showwarning(localisation.name_resolver.get("messagebox_error"), "Nieprawidłowy czas.")

    def _get_filtered_annotations(self, all_anns, current_chosen_sample, current_filter, filter_all_text):
        """
        Returns a list of annotations filtered by the current filter and AI mode.
        """
        active_origin = next((a.annotation_origin for a in all_anns if a.sample_index == current_chosen_sample), None)
        is_ai_mode = (active_origin == EAnnotationOrigin.ANALYSIS)

        filtered = []
        for ann in all_anns:
            ann_filter_val = ann.get_filter_type()
            matches_filter = (current_filter in ("", filter_all_text) or ann_filter_val == current_filter)
            is_ai_ann = (ann.annotation_origin == EAnnotationOrigin.ANALYSIS)

            if matches_filter and (is_ai_ann == is_ai_mode):
                filtered.append(ann)

        return filtered

    def _find_target_annotation(self, filtered_anns, current_chosen_sample, direction):
        """
        Finds the target annotation based on the current chosen sample and navigation direction.
        """
        current_idx = next((i for i, ann in enumerate(filtered_anns) if ann.sample_index == current_chosen_sample), -1)

        if current_idx == -1:
            current_start_sample = self.navigation_manager.current_sample
            for i, ann in enumerate(filtered_anns):
                if ann.sample_index >= current_start_sample:
                    return filtered_anns[i if direction == 1 else max(0, i - 1)]
            return filtered_anns[-1]

        target_idx = max(0, min(current_idx + direction, len(filtered_anns) - 1))
        return filtered_anns[target_idx]