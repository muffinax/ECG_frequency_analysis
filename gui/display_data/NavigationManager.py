import localisation


class NavigationManager:
    def __init__(self):
        self.current_sample: float = 0.0
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

    def previous_window(self):
        step_sec = self.window_size_sec - self.overlap_sec
        if step_sec <= 0:
            step_sec = self.window_size_sec

        step_samples = int(round(step_sec * self.current_fs))

        if self.current_sample - step_samples >= 0:
            self.current_sample -= step_samples
        else:
            self.current_sample = 0

    def next_window(self):
        window_samples = int(round(self.window_size_sec * self.current_fs))
        # WYMUSZAMY INT:
        last_possible_start = int(max(0, self.total_samples - window_samples))

        if self.current_sample >= last_possible_start:
            self.current_sample = last_possible_start
            return

        step_sec = self.window_size_sec - self.overlap_sec
        if step_sec <= 0:
            step_sec = self.window_size_sec

        # WYMUSZAMY INT (tutaj brakowało):
        step_samples = int(round(step_sec * self.current_fs))
        new_sample = self.current_sample + step_samples

        # Sprawdzamy, czy nowa pozycja nie przekracza ostatniego możliwego okna
        if new_sample > last_possible_start:
            self.current_sample = last_possible_start
        else:
            self.current_sample = new_sample

    def jump_to_time_string(self, input_str: str):
        clean_input = input_str.strip().replace(',', '.')

        try:
            target_seconds = float(clean_input)
            # WYMUSZAMY INT:
            target_sample = int(round(target_seconds * self.current_fs))

            window_samples = int(round(self.window_size_sec * self.current_fs))
            last_possible_start = int(max(0, self.total_samples - window_samples))

            if target_sample < 0:
                self.current_sample = 0
            elif target_sample > last_possible_start:
                self.current_sample = last_possible_start
            else:
                self.current_sample = target_sample

        except ValueError:
            raise ValueError(localisation.NameResolver("messagebox_error"))

    def get_current_time_string(self) -> str:
        if self.current_fs > 0:
            current_time_seconds = self.current_sample / self.current_fs
        else:
            current_time_seconds = 0.0
        return f"{current_time_seconds:.2f}"

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

    def center_on_sample(self, target_sample: float):
        if self.current_fs <= 0:
            return

        window_samples = self.window_size_sec * self.current_fs
        # Ustawiamy początek okna tak, żeby adnotacja wypadła w połowie szerokości
        new_start = target_sample - (window_samples / 2.0)

        last_possible_start = max(0.0, float(self.total_samples) - window_samples)

        # Pilnujemy, żeby nie wyjść na "minusy" ani poza koniec pliku
        if new_start < 0:
            self.current_sample = 0.0
        elif new_start > last_possible_start:
            self.current_sample = last_possible_start
        else:
            self.current_sample = new_start