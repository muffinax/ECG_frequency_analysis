from enum import Enum

class EAnnotationOrigin(Enum):
    EXTERNAL = 0
    ANALYSIS = 1
    DOCTOR = 2

    def to_string(self) -> str:
        return self.name
