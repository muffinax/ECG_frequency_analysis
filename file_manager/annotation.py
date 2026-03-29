from dataclasses import dataclass

from .e_annotation_type import EAnnotationType
from .e_lead_type import ELeadType

import localisation


@dataclass
class Annotation:
    sample_index: int
    annotation_type: EAnnotationType
    auxiliary_note: str
    channel: ELeadType | None
    subtype: int = 0
    numeric_value: int = 0
    custom_label: str | None = None

    def get_display_name(self, name_resolver: localisation.NameResolver) -> str:
        """
        Returns the localized name or the custom label if the type is CUSTOM.

        Args:
            name_resolver: localisation.NameResolver instance
        """
        if self.annotation_type == EAnnotationType.CUSTOM and self.custom_label:
            return self.custom_label

        return name_resolver.get_enum(self.annotation_type)
