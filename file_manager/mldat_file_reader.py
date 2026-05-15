import os
import pickle
from typing import TYPE_CHECKING, Any

from .base_ecg_reader import BaseECGReader
from .machine_learning_data import MachineLearningData
from .e_annotation_type import EAnnotationType
from .e_annotation_origin import EAnnotationOrigin
from .input_manager_exception import InputManagerException

if TYPE_CHECKING:
    from .file_manager import FileManager


class MLDatFileReader(BaseECGReader):
    def read(self, filepath: str, file_manager: "FileManager") -> None:
        if not os.path.exists(filepath):
            return

        try:
            with open(filepath, 'rb') as f:
                records: list[dict[str, Any]] = pickle.load(f)

            file_manager.machine_learning_data = []
            for rec in records:
                mld = MachineLearningData(
                    original_filename=rec['original_filename'],
                    signal_sample_index_start=rec['signal_sample_index_start'],
                    signal_duration=rec['signal_duration'],
                    signal_name=rec['signal_name'],
                    signal_fft=rec['signal_fft'],
                    annotations=rec.get('annotations')
                )
                file_manager.machine_learning_data.append(mld)

            file_manager.b_ml_opened = True

        except Exception as e:
            raise InputManagerException(
                error_id="mldat_read_error",
                error_description=f"Nie udało się odczytać pliku .mldat: {str(e)}"
            )

    def write(self, filepath: str, file_manager: "FileManager") -> None:
        existing_records = []

        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    existing_records = pickle.load(f)
            except Exception:
                pass

        records_dict = {}
        for rec in existing_records:
            key = (rec['original_filename'], rec['signal_sample_index_start'], rec['signal_duration'],
                   rec['signal_name'])
            records_dict[key] = rec

        ignored_types = [EAnnotationType.NORMAL_BEAT, EAnnotationType.EDF, EAnnotationType.UNKNOWN]

        for mld in file_manager.machine_learning_data:
            if mld.annotations is None and mld.original_filename == file_manager.filepath:
                extracted_annotations = []
                for ann in file_manager.annotations:
                    if getattr(ann, 'annotation_origin', None) != EAnnotationOrigin.EXTERNAL:
                        continue

                    if ann.annotation_type in ignored_types:
                        continue

                    if ann.channel is not None and ann.channel != mld.signal_name:
                        continue

                    if mld.signal_sample_index_start <= ann.sample_index < (
                            mld.signal_sample_index_start + mld.signal_duration):
                        extracted_annotations.append({
                            "annotation_type": ann.annotation_type.value,
                            "custom_label": ann.custom_label
                        })
                annotations_to_save = extracted_annotations
            elif mld.annotations is not None or (mld.annotations is None and (mld.original_filename, mld.signal_sample_index_start, mld.signal_duration, mld.signal_name) not in records_dict.keys()):
                annotations_to_save = mld.annotations
            else:
                continue

            record = {
                "original_filename": mld.original_filename,
                "signal_sample_index_start": mld.signal_sample_index_start,
                "signal_duration": mld.signal_duration,
                "signal_name": mld.signal_name,
                "signal_fft": mld.signal_fft,
                "annotations": annotations_to_save
            }

            key = (mld.original_filename, mld.signal_sample_index_start, mld.signal_duration, mld.signal_name)
            if mld.original_filename == file_manager.filepath or mld.annotations is not None:
                records_dict[key] = record

        try:
            with open(filepath, 'wb') as f:
                pickle.dump(list(records_dict.values()), f)
        except Exception as e:
            raise InputManagerException(
                error_id="mldat_save_error",
                error_description=f"Nie udało się zapisać pliku .mldat: {str(e)}"
            )