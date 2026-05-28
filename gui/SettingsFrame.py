import tkinter as tk
from tkinter import messagebox

import localisation
from file_manager import FileManager, Annotation, EAnnotationType, EAnnotationOrigin
from display_data import DisplayManager
from display_data import NavigationManager
from processor.preproc_manager import PreprocManager


class SettingsFrame(tk.Frame):
    def __init__(self, master, navigation_manager: NavigationManager, display_manager: DisplayManager, preproc_manager: PreprocManager, file_manager: FileManager,
                 on_update_callback, on_prev_annotation_callback=None, on_next_annotation_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.navigation_manager = navigation_manager
        self.display_manager = display_manager
        self.preproc_manager = preproc_manager
        self.file_manager = file_manager
        self.on_update_callback = on_update_callback
        self.on_prev_annotation_callback = on_prev_annotation_callback
        self.on_next_annotation_callback = on_next_annotation_callback

        btn_container=tk.Frame(self, bg=self['bg'])
        btn_container.pack(expand=True)

        self.to_start_button = tk.Button(btn_container, text="\u23EE", font=("Arial", 16), cursor="hand2",
                                        command=self._cmd_start)
        self.previous_button = tk.Button(btn_container, text="\u23EA", font=("Arial", 16), cursor="hand2",
                                         command=self._cmd_prev_ann)
        self.move_left_button = tk.Button(btn_container, text="\u25C0", font=("Arial", 16), cursor="hand2",
                                          command=self._cmd_left)
        self.play_pause_button = tk.Button(btn_container, text="\u25B6 / \u23F8", font=("Arial", 16), cursor="hand2",
                                           command=self._cmd_play_pause)
        self.move_right_button = tk.Button(btn_container, text="\u25B6", font=("Arial", 16), cursor="hand2",
                                           command=self._cmd_right)
        self.next_button = tk.Button(btn_container, text="\u23E9", font=("Arial", 16), cursor="hand2",
                                     command=self._cmd_next_ann)
        self.to_end_button = tk.Button(btn_container, text="\u23ED", font=("Arial", 16), cursor="hand2",
                                       command=self._cmd_end)

        time_container = tk.Frame(self, bg=self['bg'])
        time_container.pack(expand=True)

        self.time_label = tk.Label(time_container, text=localisation.name_resolver.get("parameters_window_time_label"), font=('calibre', 10, 'normal'))
        self.time_entry = tk.Entry(time_container, width=8, justify=tk.CENTER, font=('calibre', 10, 'normal'))
        self.time_go_button = tk.Button(
            time_container,
            text=localisation.name_resolver.get("parameters_window_go_button"),
            font=('calibre', 10, 'normal'),
            cursor="hand2",
            command=self._cmd_go_time)


        # self.add_annotation_button = tk.Button(btn_container, text="+ Add annotation", cursor="hand2", background="lightblue", command=None)
        self.add_signal_button = tk.Button(btn_container, text="+ Add signal", cursor="hand2", background="lightblue", command=self._cmd_add_signal)


        self.to_start_button.pack(side=tk.LEFT, padx=2)
        self.previous_button.pack(side=tk.LEFT, padx=2)
        self.move_left_button.pack(side=tk.LEFT, padx=2)
        self.play_pause_button.pack(side=tk.LEFT, padx=2)
        self.move_right_button.pack(side=tk.LEFT, padx=2)
        self.next_button.pack(side=tk.LEFT, padx=2)
        self.to_end_button.pack(side=tk.LEFT, padx=2)
        # self.add_annotation_button.pack(side=tk.LEFT, padx=(10))
        # self.add_signal_button.pack(side=tk.LEFT)

        self.time_label.pack(side=tk.LEFT, padx=2)
        self.time_entry.pack(side=tk.LEFT, padx=2)
        self.time_go_button.pack(side=tk.LEFT, padx=2)

    def _cmd_start(self):
        self.navigation_manager.jump_to_start()
        self.on_update_callback()

    def _cmd_left(self):
        self.navigation_manager.previous_window()
        self.on_update_callback()

    def _cmd_right(self):
        self.navigation_manager.next_window()
        self.on_update_callback()

    def _cmd_end(self):
        self.navigation_manager.jump_to_end()
        self.on_update_callback()

    def _cmd_go_time(self):
        user_input = self.time_entry.get()
        try:
            self.navigation_manager.jump_to_time_string(user_input)
            self.on_update_callback()
        except ValueError:
            messagebox.showwarning(localisation.name_resolver.get("messagebox_error"))

    def update_time_display(self, current_time_str: str):
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, current_time_str)

    def _cmd_play_pause(self):
        is_playing = self.navigation_manager.toggle_playback()

        if is_playing:
            self._playback_loop()

    def _playback_loop(self):
        delay_ms = 50
        delta_sec = delay_ms / 1000.0

        if self.navigation_manager.is_playing:
            has_moved = self.navigation_manager.step_playback(delta_sec)

            if has_moved:
                self.on_update_callback()
                self.after(delay_ms, self._playback_loop)

    def _cmd_prev_ann(self):
        if self.on_prev_annotation_callback:
            self.on_prev_annotation_callback()

    def _cmd_next_ann(self):
        if self.on_next_annotation_callback:
            self.on_next_annotation_callback()

    def _cmd_add_signal(self):

        filename = "Nieznany"
        if self.file_manager.filepath:
            filename = self.file_manager.filepath

        for lead in self.display_manager.displayed_leads:

            signal = self.file_manager.get_signal(channel=lead)

            ml_data_list = self.preproc_manager.get_stft_whole(signal, filename, lead)

            for ml_data in ml_data_list:
                self.file_manager.machine_learning_data.append(ml_data)

                sample_idx = int(ml_data.signal_sample_index_start * self.file_manager.sampling_frequency)

                new_ann = Annotation(
                    sample_index=sample_idx,
                    annotation_type=EAnnotationType.CUSTOM,
                    auxiliary_note="Początek okna STFT",
                    channel=lead,
                    custom_label="ML_WINDOW",
                    annotation_duration=int(ml_data.signal_duration * self.file_manager.sampling_frequency),
                    annotation_origin=EAnnotationOrigin.ANALYSIS
                )
                self.file_manager.add_annotation(new_ann)
        self.on_update_callback()

    def set_developer_mode(self, is_dev: bool):
        if is_dev:
            self.add_signal_button.pack(side=tk.LEFT)
        else:
            self.add_signal_button.pack_forget()