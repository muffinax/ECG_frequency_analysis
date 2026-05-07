import os
import pyedflib
import numpy as np
from datetime import datetime
from typing import TYPE_CHECKING

from .base_ecg_reader import BaseECGReader
from .e_annotation_type import EAnnotationType
from .annotation import Annotation
from .input_manager_exception import InputManagerException

if TYPE_CHECKING:
    from .file_manager import FileManager


class EDFReader(BaseECGReader):

    def read(self, filepath: str, file_manager: "FileManager") -> None:
        file_manager.clear()
        try:
            with pyedflib.EdfReader(filepath) as edf_record:

                try:
                    file_manager.base_datetime = edf_record.getStartdatetime()
                except Exception:
                    file_manager.base_datetime = None

                parsed_comments: dict[str, str] = {
                    "patient_code": str(edf_record.getPatientCode()),
                    "patient_additional": str(edf_record.getPatientAdditional()),
                    "equipment": str(edf_record.getEquipment()),
                    "recording_additional": str(edf_record.getRecordingAdditional())
                }
                file_manager.comments = {key: value for key, value in parsed_comments.items() if value.strip()}

                file_manager.signals.clear()
                total_channels: int = edf_record.signals_in_file
                base_sampling_frequency: float | None = None

                for index in range(total_channels):
                    lead_name: str = edf_record.getLabel(index).strip()

                    channel_data: np.ndarray = edf_record.readSignal(index)
                    channel_unit: str = edf_record.getPhysicalDimension(index).strip().lower()
                    channel_fs: float = edf_record.getSampleFrequency(index)

                    if base_sampling_frequency is None and channel_fs > 0:
                        base_sampling_frequency = channel_fs

                    if channel_unit == "v":
                        channel_data = channel_data * 1000.0
                    elif channel_unit in ["uv", "u"]:
                        channel_data = channel_data / 1000.0

                    file_manager.signals[lead_name] = channel_data

                if base_sampling_frequency is None or base_sampling_frequency <= 0:
                    raise InputManagerException(
                        error_id="edf_missing_sampling_frequency",
                        error_description="Could not determine a valid sampling frequency from any of the EDF channels."
                    )

                file_manager.sampling_frequency = base_sampling_frequency

                file_manager.annotations.clear()
                try:
                    annotation_starts, annotation_durations, annotation_labels = edf_record.readAnnotations()

                    if len(annotation_starts) > 0:
                        for index_value in range(len(annotation_starts)):
                            start_seconds: float = float(annotation_starts[index_value])
                            duration_seconds: float = float(annotation_durations[index_value]) if annotation_durations[
                                index_value] else 0.0

                            raw_label = annotation_labels[index_value]
                            label_str: str = raw_label.decode('utf-8') if isinstance(raw_label, bytes) else str(
                                raw_label)

                            sample_index: int = int(start_seconds * file_manager.sampling_frequency)

                            parsed_annotation: Annotation = Annotation(
                                sample_index=sample_index,
                                annotation_type=EAnnotationType.EDF,
                                auxiliary_note=label_str,
                                channel=None,
                                subtype=0,
                                numeric_value=int(duration_seconds * 1000),
                                custom_label=label_str.strip()
                            )
                            file_manager.annotations.append(parsed_annotation)

                except Exception:
                    pass

        except InputManagerException as exception_object:
            file_manager.clear()
            raise exception_object
        except Exception as exception_object:
            file_manager.clear()
            raise InputManagerException(
                error_id="edf_read_error",
                error_description=f"Failed to read EDF file: {str(exception_object)}"
            )

        file_manager.b_opened = True