import os
import wfdb
import numpy as np
from datetime import datetime, time, date
from typing import TYPE_CHECKING

from . import EAnnotationOrigin
from .base_ecg_reader import BaseECGReader
from .e_annotation_type import EAnnotationType
from .annotation import Annotation
from .input_manager_exception import InputManagerException

if TYPE_CHECKING:
    from .file_manager import FileManager


class WFDBReader(BaseECGReader):

    def read(self, filepath: str, file_manager: "FileManager") -> None:
        file_manager.clear()
        file_manager.filepath = filepath
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

                custom_labels_list: list[str] | None = getattr(wfdb_annotation, "custom_labels", None)

                for index_value in range(total_annotations):
                    note_value: str = wfdb_annotation.aux_note[index_value] if wfdb_annotation.aux_note[
                                                                                   index_value] is not None else ""
                    raw_channel_index: int = wfdb_annotation.chan[index_value]

                    assigned_lead_type: str | None = None
                    if raw_channel_index < len(wfdb_record.sig_name):
                        assigned_lead_type = wfdb_record.sig_name[raw_channel_index]

                    parsed_subtype: int = int(subtype_array[index_value]) if subtype_array is not None else 0
                    parsed_numeric: int = int(numeric_array[index_value]) if numeric_array is not None else 0

                    sym = wfdb_annotation.symbol[index_value]
                    ann_type = EAnnotationType.from_string(sym)

                    parsed_custom_label: str | None = None

                    if custom_labels_list is not None and len(custom_labels_list) > 0:
                        if sym == '"' and 0 <= parsed_numeric < len(custom_labels_list):
                            parsed_custom_label = custom_labels_list[parsed_numeric]
                            ann_type = EAnnotationType.CUSTOM
                            parsed_numeric = 0

                    annotation_duration = 0
                    annotation_origin = getattr(EAnnotationOrigin, "EXTERNAL", EAnnotationOrigin(0))

                    rest_note = note_value
                    if rest_note.startswith("ECG"):
                        for length in [8, 7, 4]:
                            if len(rest_note) >= length:
                                if len(rest_note) == length or rest_note[length] == ' ':
                                    possible_token = rest_note[3:length]
                                    if all(0x20 <= ord(c) <= 0x3F for c in possible_token):
                                        token = possible_token
                                        rest_note = rest_note[length + 1:] if len(rest_note) > length else ""

                                        dur_val = 0
                                        orig_val = 0
                                        parsed_correctly = False

                                        if len(token) == 5:
                                            for c in token[:4]:
                                                dur_val = (dur_val << 5) | (ord(c) & 0x1F)
                                            orig_val = ord(token[4]) & 0x1F
                                            parsed_correctly = True
                                        elif len(token) == 4:
                                            for c in token[:4]:
                                                dur_val = (dur_val << 5) | (ord(c) & 0x1F)
                                            parsed_correctly = True
                                        elif len(token) == 1:
                                            orig_val = ord(token[0]) & 0x1F
                                            parsed_correctly = True

                                        if parsed_correctly:
                                            annotation_duration = dur_val
                                            try:
                                                annotation_origin = EAnnotationOrigin(orig_val)
                                            except ValueError:
                                                pass
                                        break

                    parsed_annotation: Annotation = Annotation(
                        sample_index=int(wfdb_annotation.sample[index_value]),
                        annotation_duration=annotation_duration,
                        annotation_origin=annotation_origin,
                        annotation_type=ann_type,
                        auxiliary_note=rest_note,
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

    def write(self, filepath: str, file_manager: "FileManager") -> None:
        record_path: str = os.path.splitext(p=filepath)[0]
        write_dir = os.path.dirname(record_path) or '.'
        rec_name = os.path.basename(record_path)

        sig_names = list(file_manager.signals.keys())
        n_sig = len(sig_names)

        comments = [f"{k}: {v}" for k, v in file_manager.comments.items()]

        base_time = file_manager.base_datetime.time() if file_manager.base_datetime is not None else None
        base_date = file_manager.base_datetime.date() if file_manager.base_datetime is not None else None

        if n_sig > 0:
            signal_values = list(file_manager.signals.values())
            p_signal = np.column_stack(signal_values)
            fmt = ["16"] * n_sig
            units = ["mV"] * n_sig

            wfdb.wrsamp(
                record_name=rec_name,
                fs=file_manager.sampling_frequency,
                units=units,
                sig_name=sig_names,
                p_signal=p_signal,
                fmt=fmt,
                comments=comments,
                base_time=base_time,
                base_date=base_date,
                write_dir=write_dir
            )
        else:
            record = wfdb.Record(
                record_name=rec_name,
                fs=file_manager.sampling_frequency,
                n_sig=0,
                comments=comments,
                base_time=base_time,
                base_date=base_date
            )
            record.wrheader(write_dir=write_dir)

        if file_manager.annotations:
            samples = []
            symbols = []
            aux_notes = []
            chans = []
            subs = []
            nums = []
            unique_labels = []

            for ann in file_manager.annotations:
                if ann.annotation_type in [EAnnotationType.EDF, EAnnotationType.UNKNOWN]:
                    continue

                samples.append(ann.sample_index)

                is_custom = (ann.annotation_type == EAnnotationType.CUSTOM and
                             ann.custom_label and ann.custom_label.strip() != "")

                if is_custom:
                    sym = '"'
                    if ann.custom_label not in unique_labels:
                        unique_labels.append(ann.custom_label)
                    label_idx = unique_labels.index(ann.custom_label)
                    nums.append(label_idx)
                else:
                    sym = '"' if ann.annotation_type == EAnnotationType.CUSTOM else str(ann.annotation_type.value)
                    if len(sym) > 1:
                        sym = '"'
                    nums.append(ann.numeric_value)

                symbols.append(sym)

                dur = getattr(ann, 'annotation_duration', 0)
                orig_val = ann.annotation_origin.value if hasattr(ann.annotation_origin, 'value') else 0

                dur_str = ""
                orig_str = ""

                if dur > 0:
                    for i in range(4):
                        val = (dur >> (15 - i * 5)) & 0x1F
                        dur_str += chr(val | 0x20)

                if orig_val > 0:
                    orig_str = chr((orig_val & 0x1F) | 0x20)

                prefix = ""
                if dur_str and orig_str:
                    prefix = f"ECG{dur_str}{orig_str}"
                elif dur_str:
                    prefix = f"ECG{dur_str}"
                elif orig_str:
                    prefix = f"ECG{orig_str}"

                final_note = ann.auxiliary_note or ""

                if is_custom:
                    if final_note:
                        final_note = f"[{ann.custom_label}] {final_note}"
                    else:
                        final_note = ann.custom_label

                if prefix:
                    final_note = f"{prefix} {final_note}".strip()

                aux_notes.append(final_note)

                chan_idx = 0
                if ann.channel in sig_names:
                    chan_idx = sig_names.index(ann.channel)
                chans.append(chan_idx)

                subs.append(ann.subtype)

            if not samples:
                return

            final_aux_notes = aux_notes if any(aux_notes) else None
            final_chans = np.array(chans) if any(chans) else None
            final_subs = np.array(subs) if any(subs) else None
            final_nums = np.array(nums) if any(nums) else None

            ann_obj = wfdb.Annotation(
                record_name=rec_name,
                extension="atr",
                sample=np.array(samples),
                symbol=symbols,
                aux_note=final_aux_notes,
                chan=final_chans,
                subtype=final_subs,
                num=final_nums,
                custom_labels=None
            )
            ann_obj.wrann(write_dir=write_dir)
