import os
import wfdb
import numpy as np
from datetime import datetime, time, date
from typing import TYPE_CHECKING

from .base_ecg_reader import BaseECGReader
from .e_annotation_type import EAnnotationType
from .annotation import Annotation
from .input_manager_exception import InputManagerException

if TYPE_CHECKING:
    from .file_manager import FileManager


class WFDBReader(BaseECGReader):

    def read(self, filepath: str, file_manager: "FileManager") -> None:
        record_path: str = os.path.splitext(p=filepath)[0]

        try:
            wfdb_record: wfdb.Record = wfdb.rdrecord(record_name=record_path)
            file_manager.sampling_frequency = float(wfdb_record.fs)
            file_manager.wfdb_record = wfdb_record

            record_date: date | None = getattr(wfdb_record, "base_date", None)
            record_time: time | None = getattr(wfdb_record, "base_time", None)

            if record_date is not None and record_time is not None:
                file_manager.base_datetime = datetime.combine(date=record_date, time=record_time)
            elif record_date is not None:
                file_manager.base_datetime = datetime.combine(date=record_date, time=time())
            else:
                file_manager.base_datetime = None

            raw_comments: list[str] = getattr(wfdb_record, "comments", [])
            parsed_comments: dict[str, str] = {}

            for comment_index, comment_string in enumerate(raw_comments):
                if ":" in comment_string:
                    split_comment: list[str] = comment_string.split(sep=":", maxsplit=1)
                    key_string: str = split_comment[0].strip()
                    value_string: str = split_comment[1].strip()
                    parsed_comments[key_string] = value_string
                else:
                    parsed_comments[f"note_{comment_index}"] = comment_string.strip()

            file_manager.comments = parsed_comments

            file_manager.signals.clear()
            record_units: list[str] = getattr(wfdb_record, "units", ["mV"] * len(wfdb_record.sig_name))

            for index, channel_name in enumerate(wfdb_record.sig_name):
                lead_type: str = channel_name
                channel_data: np.ndarray = wfdb_record.p_signal[:, index]
                channel_unit: str = record_units[index].strip().lower() if record_units[index] else "mv"

                if channel_unit == "v":
                    channel_data = channel_data * 1000.0
                elif channel_unit == "uv":
                    channel_data = channel_data / 1000.0
                elif channel_unit == "u":
                    channel_data = channel_data / 1000.0

                file_manager.signals[lead_type] = channel_data

            try:
                wfdb_annotation: wfdb.Annotation = wfdb.rdann(record_name=record_path, extension="atr")
                file_manager.wfdb_annotation = wfdb_annotation
                file_manager.annotations.clear()

                total_annotations: int = len(wfdb_annotation.sample)
                subtype_array: np.ndarray | list[int] = getattr(wfdb_annotation, "sub", [0] * total_annotations)
                numeric_array: np.ndarray | list[int] = getattr(wfdb_annotation, "num", [0] * total_annotations)
                custom_labels_array: np.ndarray | list[str | None] = getattr(wfdb_annotation, "custom_labels",
                                                                             [None] * total_annotations)

                for index_value in range(total_annotations):
                    note_value: str = wfdb_annotation.aux_note[index_value] if wfdb_annotation.aux_note[
                                                                                   index_value] is not None else ""
                    raw_channel_index: int = wfdb_annotation.chan[index_value]

                    assigned_lead_type: str | None = None
                    if raw_channel_index < len(wfdb_record.sig_name):
                        assigned_lead_type = wfdb_record.sig_name[raw_channel_index]

                    parsed_subtype: int = int(subtype_array[index_value]) if subtype_array is not None else 0
                    parsed_numeric: int = int(numeric_array[index_value]) if numeric_array is not None else 0
                    parsed_custom_label: str | None = custom_labels_array[
                        index_value] if custom_labels_array is not None else None

                    parsed_annotation: Annotation = Annotation(
                        sample_index=int(wfdb_annotation.sample[index_value]),
                        annotation_type=EAnnotationType.from_string(wfdb_annotation.symbol[index_value]),
                        auxiliary_note=note_value,
                        channel=assigned_lead_type,
                        subtype=parsed_subtype,
                        numeric_value=parsed_numeric,
                        custom_label=parsed_custom_label
                    )
                    file_manager.annotations.append(parsed_annotation)

            except FileNotFoundError:
                file_manager.wfdb_annotation = None

        except Exception as exception_object:
            file_manager.clear()
            raise InputManagerException(
                error_id="wfdb_read_error",
                error_description=f"Failed to read WFDB file: {str(exception_object)}"
            )

        file_manager.b_opened = True
