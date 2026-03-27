from enum import Enum

class EVoltageUnit(Enum):
    VOLTS = "V"
    MILLIVOLTS = "mV"
    MICROVOLTS = "uV"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, string_value: str) -> "EVoltageUnit":
        for unit in cls:
            if unit.value.lower() == string_value.lower():
                return unit
        return cls.UNKNOWN

    def to_string(self) -> str:
        return self.value