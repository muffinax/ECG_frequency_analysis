import os
import pickle
from typing import TYPE_CHECKING, Any

from file_manager import MachineLearningData
from file_manager import InputManagerException

def folder_reader(folder_path: str) -> list[MachineLearningData]:
    all_data: list[MachineLearningData] = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if not file.endswith(".mldat"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'rb') as f:
                    records: list[dict[str, Any]] = pickle.load(f)

                for rec in records:
                    mld = MachineLearningData(
                        original_filename=rec['original_filename'],
                        signal_sample_index_start=rec['signal_sample_index_start'],
                        signal_duration=rec['signal_duration'],
                        signal_name=rec['signal_name'],
                        signal_fft_freqs=rec['signal_fft_freqs'],
                        signal_fft=rec['signal_fft'],
                        signal_sampling_frequency=rec['signal_sampling_frequency'],
                        annotations=rec.get('annotations')
                    )
                    all_data.append(mld)
            except Exception as e:
                raise InputManagerException(
                    error_id="mldat_read_error",
                    error_description=f"Nie udało się odczytać pliku .mldat: {str(e)}"
                )
    return all_data