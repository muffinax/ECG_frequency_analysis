import os
import pickle
from typing import TYPE_CHECKING, Any

from file_manager import MachineLearningData
from file_manager import InputManagerException

print("Reading file...")

if not os.path.exists("C:/Users/froma/Downloads/mit-bih-arrhythmia-database-1.0.0-20260518T190848Z-3-001/mit-bih-arrhythmia-database-1.0.0/102/102.mldat"):
    raise FileNotFoundError("C:/Users/froma/Downloads/mit-bih-arrhythmia-database-1.0.0-20260518T190848Z-3-001/mit-bih-arrhythmia-database-1.0.0/102/102.mldat")

try:
    print("Start read()")
    with open("C:/Users/froma/Downloads/mit-bih-arrhythmia-database-1.0.0-20260518T190848Z-3-001/mit-bih-arrhythmia-database-1.0.0/102/102.mldat", 'rb') as f:
        records: list[dict[str, Any]] = pickle.load(f)
        print("Loaded records:", type(records), len(records))

    machine_learning_data = []
    for rec in records:
        mld = MachineLearningData(
            original_filename=rec['original_filename'],
            signal_sample_index_start=rec['signal_sample_index_start'],
            signal_duration=rec['signal_duration'],
            signal_name=rec['signal_name'],
            signal_fft=rec['signal_fft'],
            signal_sampling_frequency=rec['signal_sampling_frequency'],
            annotations=rec.get('annotations')
        )
        machine_learning_data.append(mld)
    print(machine_learning_data[0].original_filename)
except Exception as e:
    raise InputManagerException(
        error_id="mldat_read_error",
        error_description=f"Nie udało się odczytać pliku .mldat: {str(e)}"
    )