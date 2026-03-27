from enum import Enum

class ELeadType(Enum):
    LEAD_I = "I"       # odprowadzenie kończynowe I
    LEAD_II = "II"     # odprowadzenie kończynowe II
    LEAD_III = "III"   # odprowadzenie kończynowe III
    LEAD_AVR = "aVR"   # wzmocnione odprowadzenie kończynowe aVR
    LEAD_AVL = "aVL"   # wzmocnione odprowadzenie kończynowe aVL
    LEAD_AVF = "aVF"   # wzmocnione odprowadzenie kończynowe aVF
    LEAD_V1 = "V1"     # przedsercowe V1
    LEAD_V2 = "V2"     # przedsercowe V2
    LEAD_V3 = "V3"     # przedsercowe V3
    LEAD_V4 = "V4"     # przedsercowe V4
    LEAD_V5 = "V5"     # przedsercowe V5
    LEAD_V6 = "V6"     # przedsercowe V6
    LEAD_MLII = "MLII" # zmodyfikowane odprowadzenie II (częste w Holterach)
    UNKNOWN = "unknown" # nieznane odprowadzenie

    @classmethod
    def from_string(cls, string_value: str) -> "ELeadType":
        for lead in cls:
            if lead.value.lower() == string_value.lower():
                return lead
        return cls.UNKNOWN

    def to_string(self) -> str:
        return self.value