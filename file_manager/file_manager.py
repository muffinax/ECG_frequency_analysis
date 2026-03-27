import os
import tkinter as tk
from tkinter import filedialog
from typing import Any
import numpy as np
import wfdb

from .e_voltage_unit import EVoltageUnit
from .e_lead_type import ELeadType
from .e_annotation_type import EAnnotationType
from .annotation import Annotation
from .input_manager_exception import InputManagerException


class FileManager:
    def __init__(self) -> None:
        self.filepath: str | None = None
        self.wfdb_record: Any | None = None
        self.wfdb_annotation: Any | None = None
        self.sampling_frequency: float = 0.0
        self.signals: dict[ELeadType, np.ndarray] = {}
        self.annotations: list[Annotation] = []

    def open_file(self, filepath: str) -> None:
        try:
            self.filepath = filepath

            # wfdb.rdrecord expects path without extension
            record_path: str = os.path.splitext(p=filepath)[0]

            self.wfdb_record = wfdb.rdrecord(record_name=record_path)
            self.sampling_frequency = float(self.wfdb_record.fs)

            self.signals.clear()
            for index, channel_name in enumerate(iterable=self.wfdb_record.sig_name):
                lead_type: ELeadType = ELeadType.from_string(string_value=channel_name)
                channel_data: np.ndarray = self.wfdb_record.p_signal[:, index]
                self.signals[lead_type] = channel_data

            try:
                self.wfdb_annotation = wfdb.rdann(record_name=record_path, extension="atr")
                self.annotations.clear()

                for i in range(len(self.wfdb_annotation.sample)):
                    note: str = self.wfdb_annotation.aux_note[i] if self.wfdb_annotation.aux_note[i] is not None else ""
                    raw_channel: int = self.wfdb_annotation.chan[i]

                    assigned_lead: ELeadType | None = None
                    if raw_channel < len(self.wfdb_record.sig_name):
                        assigned_lead = ELeadType.from_string(string_value=self.wfdb_record.sig_name[raw_channel])

                    parsed_annotation = Annotation(
                        sample_index=int(self.wfdb_annotation.sample[i]),
                        annotation_type=EAnnotationType.from_string(string_value=self.wfdb_annotation.symbol[i]),
                        auxiliary_note=note,
                        channel=assigned_lead
                    )
                    self.annotations.append(parsed_annotation)
            except FileNotFoundError:
                pass  # It's okay if annotations don't exist

        except Exception as exception_object:
            raise InputManagerException(
                error_id="file_read_error",
                error_description=f"Failed to read file: {str(object=exception_object)}"
            )

    def open_file_system_gui(self) -> None:
        try:
            root_window: tk.Tk = tk.Tk()
            root_window.withdraw()

            selected_filepath: str = filedialog.askopenfilename(
                parent=root_window,
                title="Select WFDB Header File",
                filetypes=[("WFDB Header", "*.hea"), ("All files", "*.*")]
            )

            if selected_filepath:
                self.open_file(filepath=selected_filepath)

        except Exception as exception_object:
            raise InputManagerException(
                error_id="gui_open_error",
                error_description=f"Failed to open file dialog: {str(object=exception_object)}"
            )

    def opened(self) -> bool:
        return self.wfdb_record is not None

    def __bool__(self) -> bool:
        return self.opened()

    def get_signal(
            self,
            channel: ELeadType,
            from_time: float | None = None,
            to_time: float | None = None,
            from_sample: int | None = None,
            to_sample: int | None = None,
            unit: EVoltageUnit = EVoltageUnit.MILLIVOLTS
    ) -> np.ndarray:

        if channel not in self.signals:
            raise InputManagerException(
                error_id="channel_not_found",
                error_description=f"Channel {channel.to_string()} is not present in this record."
            )

        signal_array: np.ndarray = self.signals[channel]
        start_index: int = 0
        end_index: int = len(signal_array)

        if from_sample is not None:
            start_index = from_sample
        elif from_time is not None:
            start_index = int(from_time * self.sampling_frequency)

        if to_sample is not None:
            end_index = to_sample
        elif to_time is not None:
            end_index = int(to_time * self.sampling_frequency)

        sliced_signal: np.ndarray = signal_array[start_index:end_index]

        # WFDB default is usually mV. Adjusting based on requested unit.
        if unit == EVoltageUnit.VOLTS:
            return sliced_signal / 1000.0
        elif unit == EVoltageUnit.MICROVOLTS:
            return sliced_signal * 1000.0

        return sliced_signal

    def get_time_axis(
            self,
            from_time: float | None = None,
            to_time: float | None = None,
            from_sample: int | None = None,
            to_sample: int | None = None,
            use_real_time: bool = False
    ) -> np.ndarray:

        start_index: int = 0
        end_index: int = 0

        if self.signals:
            first_key: ELeadType = list(self.signals.keys())[0]
            end_index = len(self.signals[first_key])

        if from_sample is not None:
            start_index = from_sample
        elif from_time is not None:
            start_index = int(from_time * self.sampling_frequency)

        if to_sample is not None:
            end_index = to_sample
        elif to_time is not None:
            end_index = int(to_time * self.sampling_frequency)

        time_axis: np.ndarray = np.arange(start=start_index, stop=end_index) / self.sampling_frequency
        return time_axis

    def get_annotations(self) -> list[Annotation]:
        return self.annotations

    def get_annotation(self, index: int) -> Annotation:
        if index < 0 or index >= len(self.annotations):
            raise InputManagerException(
                error_id="annotation_index_error",
                error_description="Annotation index out of bounds."
            )
        return self.annotations[index]

    def add_annotation(self, new_annotation: Annotation) -> None:
        self.annotations.append(new_annotation)
        # Sort annotations by sample_index to keep time-series order intact
        self.annotations.sort(key=lambda annotation_obj: annotation_obj.sample_index)

    def remove_annotation(self, index: int) -> None:
        if index < 0 or index >= len(self.annotations):
            raise InputManagerException(
                error_id="annotation_index_error",
                error_description="Annotation index out of bounds."
            )
        self.annotations.pop(index)