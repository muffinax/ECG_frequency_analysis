from enum import Enum

class EAnnotationType(Enum):
    NORMAL_BEAT = "N"                                  # uderzenie prawidłowe
    LEFT_BUNDLE_BRANCH_BLOCK = "L"                     # blok lewej odnogi pęczka Hisa
    RIGHT_BUNDLE_BRANCH_BLOCK = "R"                    # blok prawej odnogi pęczka Hisa
    BUNDLE_BRANCH_BLOCK = "B"                          # blok odnogi pęczka Hisa (nieokreślony)
    ATRIAL_PREMATURE_BEAT = "A"                        # przedwczesne pobudzenie przedsionkowe
    ABERRATED_ATRIAL_PREMATURE_BEAT = "a"              # aberrantne przedwczesne pobudzenie przedsionkowe
    NODAL_PREMATURE_BEAT = "J"                         # przedwczesne pobudzenie węzłowe
    SUPRAVENTRICULAR_PREMATURE_BEAT = "S"              # przedwczesne pobudzenie nadkomorowe
    PREMATURE_VENTRICULAR_CONTRACTION = "V"            # przedwczesny skurcz komorowy
    R_ON_T_PREMATURE_VENTRICULAR_CONTRACTION = "r"     # przedwczesny skurcz komorowy typu R-na-T
    FUSION_VENTRICULAR_AND_NORMAL = "F"                # pobudzenie zsumowane (komorowe i prawidłowe)
    ATRIAL_ESCAPE_BEAT = "e"                           # pobudzenie zastępcze przedsionkowe
    NODAL_ESCAPE_BEAT = "j"                            # pobudzenie zastępcze węzłowe
    SUPRAVENTRICULAR_ESCAPE_BEAT = "n"                 # pobudzenie zastępcze nadkomorowe
    VENTRICULAR_ESCAPE_BEAT = "E"                      # pobudzenie zastępcze komorowe
    PACED_BEAT = "/"                                   # uderzenie stymulowane
    FUSION_PACED_AND_NORMAL = "f"                      # pobudzenie zsumowane (stymulowane i prawidłowe)
    UNCLASSIFIABLE_BEAT = "Q"                          # uderzenie niesklasyfikowane
    BEAT_NOT_CLASSIFIED_DURING_LEARNING = "?"          # uderzenie niesklasyfikowane (podczas uczenia algorytmu)
    START_VENTRICULAR_FLUTTER_FIBRILLATION = "["       # początek trzepotania/migotania komór
    VENTRICULAR_FLUTTER_WAVE = "!"                     # fala trzepotania komór
    END_VENTRICULAR_FLUTTER_FIBRILLATION = "]"         # koniec trzepotania/migotania komór
    NON_CONDUCTED_P_WAVE = "x"                         # zablokowany załamek P (bez przewodzenia)
    WAVEFORM_ONSET = "("                               # początek fali/załamka
    WAVEFORM_END = ")"                                 # koniec fali/załamka
    PEAK_P_WAVE = "p"                                  # szczyt załamka P
    PEAK_T_WAVE = "t"                                  # szczyt załamka T
    PEAK_U_WAVE = "u"                                  # szczyt załamka U
    PQ_JUNCTION = "`"                                  # złącze PQ
    J_POINT = "'"                                      # punkt J
    NON_CAPTURED_PACEMAKER_ARTIFACT = "^"              # artefakt stymulatora (bez przechwycenia)
    ISOLATED_QRS_LIKE_ARTIFACT = "|"                   # izolowany artefakt przypominający zespół QRS
    CHANGE_IN_SIGNAL_QUALITY = "~"                     # zmiana jakości sygnału / artefakt
    RHYTHM_CHANGE = "+"                                # zmiana rytmu serca
    ST_SEGMENT_CHANGE = "s"                            # zmiana odcinka ST
    T_WAVE_CHANGE = "T"                                # zmiana załamka T
    SYSTOLE = "*"                                      # skurcz
    DIASTOLE = "D"                                     # rozkurcz
    MEASUREMENT_ANNOTATION = "="                       # adnotacja pomiarowa
    COMMENT_ANNOTATION = '"'                           # komentarz
    LINK_TO_EXTERNAL_DATA = "@"                        # odnośnik do danych zewnętrznych
    CUSTOM = "CUS"                                  # adnotacja wlasna
    UNKNOWN = "UNK"                                # nieznany typ adnotacji

    @classmethod
    def from_string(cls, string_value: str) -> "EAnnotationType":
        for annotation_type in cls:
            if annotation_type.value == string_value:
                return annotation_type
        return cls.UNKNOWN

    def to_string(self) -> str:
        return self.value
