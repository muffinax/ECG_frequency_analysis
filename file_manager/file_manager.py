import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from typing import Any
import numpy as np

from .base_ecg_reader import BaseECGReader
from .e_voltage_unit import EVoltageUnit
from .annotation import Annotation
from .input_manager_exception import InputManagerException

from .wfdb_reader import WFDBReader
from .edf_reader import EDFReader
from .mldat_file_reader import MLDatFileReader

from .machine_learning_data import MachineLearningData

import traceback


class FileManager:
    def __init__(self) -> None:
        self.b_opened: bool = False
        self.filepath: str | None = None
        self.wfdb_record: Any | None = None
        self.wfdb_annotation: Any | None = None
        self.sampling_frequency: float = 0.0
        self.base_datetime: datetime | None = None
        self.comments: dict[str, str] = {}
        self.signals: dict[str, np.ndarray] = {}
        self.annotations: list[Annotation] = []
        self.b_ml_opened: bool = False
        self.machine_learning_data: list[MachineLearningData] = []

    def _get_reader_for_file(self, filepath: str) -> BaseECGReader:
        file_extension: str = os.path.splitext(p=filepath)[1].lower()

        if file_extension in ['.hea', '.dat', '.atr']:
            return WFDBReader()
        elif file_extension in ['.edf']:
            return EDFReader()
        elif file_extension in ['.mldat']:
            return MLDatFileReader()
        else:
            raise InputManagerException(
                error_id="unsupported_file_type",
                error_description=f"File extension '{file_extension}' is not supported."
            )

    def open_file(self, filepath: str) -> None:
        try:
            self.filepath = filepath
            reader_instance: BaseECGReader = self._get_reader_for_file(filepath=filepath)
            reader_instance.read(filepath=filepath, file_manager=self)

        except Exception as exception_object:
            raise InputManagerException(
                error_id="file_read_error",
                error_description=f"Failed to process file: {str(object=exception_object)}"
            )

    def open_file_system_gui(self) -> None:
        try:
            root_window: tk.Tk = tk.Tk()
            root_window.withdraw()

            selected_filepath: str = filedialog.askopenfilename(
                parent=root_window,
                title="Select input ECG file",
                filetypes=[("WFDB Header", "*.hea"), ("EDF", "*.edf"), ("MLDat", "*.mldat"), ("All files", "*.*")]
            )

            if selected_filepath:
                self.open_file(filepath=selected_filepath)

        except Exception as exception_object:
            raise InputManagerException(
                error_id="gui_open_error",
                error_description=f"Failed to open file dialog: {str(object=exception_object)}"
            )

    def opened(self) -> bool:
        return self.b_opened

    def __bool__(self) -> bool:
        return self.opened()

    def get_sample(
            self,
            relative_time: float | None = None,
            real_time: datetime | None = None
    ) -> int:

        if relative_time is not None:
            return int(round(number=relative_time * self.sampling_frequency))

        elif real_time is not None:
            if self.base_datetime is None:
                raise InputManagerException(
                    error_id="missing_base_time",
                    error_description="Cannot calculate sample from real time because base_datetime is not set."
                )
            time_difference_seconds: float = (real_time - self.base_datetime).total_seconds()
            return int(round(number=time_difference_seconds * self.sampling_frequency))

        else:
            raise InputManagerException(
                error_id="missing_arguments",
                error_description="Either relative_time or real_time must be provided."
            )

    def get_available_leads(self) -> list[str]:
        return list(self.signals.keys())

    def get_signal(
            self,
            channel: str,
            from_sample: int | None = None,
            to_sample: int | None = None,
            unit: EVoltageUnit = EVoltageUnit.MILLIVOLTS
    ) -> np.ndarray:

        if channel not in self.signals:
            raise InputManagerException(
                error_id="channel_not_found",
                error_description=f"Channel {channel} is not present in this record."
            )

        signal_array: np.ndarray = self.signals[channel]
        start_index: int = 0
        end_index: int = len(signal_array)

        if from_sample is not None:
            start_index = from_sample

        if to_sample is not None:
            end_index = to_sample

        sliced_signal: np.ndarray = signal_array[start_index:end_index]

        if unit == EVoltageUnit.VOLTS:
            return sliced_signal / 1000.0
        elif unit == EVoltageUnit.MICROVOLTS:
            return sliced_signal * 1000.0

        return sliced_signal

    def get_time_axis(
            self,
            from_sample: int | None = None,
            to_sample: int | None = None,
            use_real_time: bool = False
    ) -> np.ndarray:

        start_index: int = 0
        end_index: int = self.get_total_samples()

        if from_sample is not None:
            start_index = from_sample

        if to_sample is not None:
            end_index = to_sample

        time_axis_relative: np.ndarray = np.arange(start=start_index, stop=end_index) / self.sampling_frequency

        if use_real_time:
            if self.base_datetime is None:
                raise InputManagerException(
                    error_id="missing_base_time",
                    error_description="Cannot generate real time axis because base_datetime is not set."
                )
            base_timestamp: float = self.base_datetime.timestamp()
            # Returns an array of UNIX timestamps (floats) which is optimal for GUI plotting libraries
            return time_axis_relative + base_timestamp

        return time_axis_relative

    def get_annotations(
            self,
            from_sample: int | None = None,
            to_sample: int | None = None
    ) -> list[Annotation]:

        filtered_annotations: list[Annotation] = []

        for annotation_object in self.annotations:
            if from_sample is not None and annotation_object.sample_index < from_sample:
                continue
            if to_sample is not None and annotation_object.sample_index > to_sample:
                continue
            filtered_annotations.append(annotation_object)

        return filtered_annotations

    def get_annotation(self, index: int) -> Annotation:
        if index < 0 or index >= len(self.annotations):
            raise InputManagerException(
                error_id="annotation_index_error",
                error_description="Annotation index out of bounds."
            )
        return self.annotations[index]

    def add_annotation(self, new_annotation: Annotation) -> None:
        self.annotations.append(new_annotation)
        self.annotations.sort(key=lambda annotation_obj: annotation_obj.sample_index)

    def remove_annotation(self, index: int) -> None:
        if index < 0 or index >= len(self.annotations):
            raise InputManagerException(
                error_id="annotation_index_error",
                error_description="Annotation index out of bounds."
            )
        self.annotations.pop(index)

    def get_total_samples(self) -> int:
        if not self.signals:
            return 0

        first_lead_key: str = list(self.signals.keys())[0]
        total_length: int = len(self.signals[first_lead_key])

        return total_length

    def get_duration_seconds(self) -> float:
        if self.sampling_frequency <= 0.0:
            return 0.0

        total_samples: int = self.get_total_samples()
        duration_in_seconds: float = total_samples / self.sampling_frequency

        return duration_in_seconds

    def clear(self) -> None:
        self.b_opened = False
        self.filepath = None
        self.wfdb_record = None
        self.wfdb_annotation = None
        self.sampling_frequency = 0.0
        self.base_datetime = None

        self.comments.clear()
        self.signals.clear()
        self.annotations.clear()

    def save_file(self, filepath: str) -> None:
        if not self.b_opened:
            raise InputManagerException(
                error_id="no_file_opened",
                error_description="Cannot save because no file is currently opened."
            )

        file_extension: str = os.path.splitext(p=filepath)[1].lower()

        if file_extension in ['.hea', '.dat', '.atr', '']:
            writer_instance = WFDBReader()
            writer_instance.write(filepath=filepath, file_manager=self)
        elif file_extension in ['.mldat']:
            writer_instance = MLDatFileReader()
            writer_instance.write(filepath=filepath, file_manager=self)
        else:
            raise InputManagerException(
                error_id="unsupported_save_format",
                error_description=f"Saving to extension '{file_extension}' is not supported yet."
            )

    def save_file_system_gui(self) -> None:
        try:
            root_window: tk.Tk = tk.Tk()
            root_window.withdraw()

            selected_filepath: str = filedialog.asksaveasfilename(
                parent=root_window,
                title="Save ECG file as",
                defaultextension=".hea",
                filetypes=[("WFDB Header", "*.hea"), ("MLDat", "*.mldat"), ("All files", "*.*")]
            )

            if selected_filepath:
                self.save_file(filepath=selected_filepath)

        except Exception as exception_object:
            traceback.print_exc()
            raise InputManagerException(
                error_id="gui_save_error",
                error_description=f"Failed to open save file dialog: {str(object=exception_object)}"
            )
