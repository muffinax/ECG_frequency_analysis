from gui.TimeConverter import TimeConverter


class NavigationManager:
    def __init__(self):
        self.current_sample: int = 0
        self.window_size_sec: float = 10.0
        self.current_fs: float = 0.0
        self.total_samples: int = 0
        self.overlap_sec: float = 1.0
        self.amplitude = 1.0

        self.is_playing: bool = False
        self.playback_speed: float = 1.0

    def reset_for_new_file(self, fs: float, total_samples: int):
        self.current_sample = 0
        self.current_fs = fs
        self.total_samples = total_samples

    def jump_to_start(self):
        self.current_sample = 0

    def jump_to_end(self):
        window_samples = int(round(self.window_size_sec * self.current_fs))

        if self.total_samples > window_samples:
            self.current_sample = self.total_samples - window_samples
        else:
            self.current_sample = 0

    def next_window(self):
        window_samples = int(round(self.window_size_sec * self.current_fs))
        if self.current_sample >= self.total_samples - window_samples:
            self.current_sample = max(0, self.total_samples - window_samples)
            return

        step_sec = self.window_size_sec - self.overlap_sec
        if step_sec <= 0:
            step_sec = self.window_size_sec

        step_samples = int(round(step_sec * self.current_fs))
        if self.current_sample + step_samples < self.total_samples:
            self.current_sample += step_samples

    def previous_window(self):
        step_sec = self.window_size_sec - self.overlap_sec
        if step_sec <= 0:
            step_sec = self.window_size_sec

        step_samples = int(round(step_sec * self.current_fs))

        if self.current_sample - step_samples >= 0:
            self.current_sample -= step_samples
        else:
            self.current_sample = 0

    def jump_to_time_string(self, time_str: str):
        target_sample = TimeConverter.time_str_to_samples(time_str, self.current_fs)

        if target_sample <= self.total_samples:
            self.current_sample = target_sample
        else:
            self.current_sample = self.total_samples

    def get_current_time_string(self) -> str:
        return TimeConverter.samples_to_time_str(self.current_sample, self.current_fs)

    def is_first_window(self) -> bool:
        return self.current_sample <= 0

    def is_last_window(self) -> bool:
        if self.current_fs <= 0.0:
            return False

        window_samples = int(round(self.window_size_sec * self.current_fs))
        return self.current_sample >= (self.total_samples - window_samples)

    def toggle_playback(self) -> bool:
        self.is_playing = not self.is_playing
        return self.is_playing

    def stop_playback(self):
        self.is_playing = False

    def step_playback(self, delta_time_sec: float) -> bool:
        if not self.is_playing or self.current_fs <= 0.0:
            return False

        step_samples = int(round(delta_time_sec * self.current_fs * self.playback_speed))

        if step_samples == 0:
            step_samples = 1

        window_samples = int(round(self.window_size_sec * self.current_fs))

        if self.current_sample + step_samples >= (self.total_samples - window_samples):
            self.current_sample = max(0, self.total_samples - window_samples)
            self.is_playing = False
            return False

        self.current_sample += step_samples
        return True