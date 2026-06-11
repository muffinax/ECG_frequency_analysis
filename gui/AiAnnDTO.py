from dataclasses import dataclass
from file_manager import Annotation

@dataclass
class AiAnnDTO:
    annotation: 'Annotation'
    is_saved: bool = True