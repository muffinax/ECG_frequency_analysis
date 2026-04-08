import localisation


class TimeConverter:
    @staticmethod
    def time_str_to_samples(time_str: str, fs: float) -> int:
        try:
            parts = time_str.strip().split(':')

            if len(parts) == 3:  # GG:MM:SS
                h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            elif len(parts) == 2:  # MM:SS
                h = 0
                m, s = int(parts[0]), int(parts[1])
            elif len(parts) == 1:  # SS
                h, m = 0, 0
                s = int(parts[0])
            else:
                raise ValueError(localisation.name_resolver.get("messagebox_error"))

            total_seconds = (h * 3600) + (m * 60) + s

            return int(round(total_seconds * fs))

        except ValueError:
            raise ValueError(localisation.name_resolver.get("messagebox_error"))


    @staticmethod
    def samples_to_time_str(samples: int, fs: float) -> str:
        if fs <= 0.0:
            return "00:00:00"

        total_seconds = int(round(samples / fs))

        h = int(total_seconds // 3600)
        m = int((total_seconds % 3600) // 60)
        s = int(total_seconds % 60)

        return f"{h:02d}:{m:02d}:{s:02d}"