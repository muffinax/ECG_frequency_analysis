from dataclasses import dataclass
from .e_annotation_type import EAnnotationType
from .e_lead_type import ELeadType

@dataclass
class Annotation:
    sample_index: int
    annotation_type: EAnnotationType
    auxiliary_note: str
    channel: ELeadType | None