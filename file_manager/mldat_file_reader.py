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
        """Odczytuje plik .mldat i ładuje jego zawartość do obiektu FileManager."""
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
                    signal_fft=rec['signal_fft']
                )
                file_manager.machine_learning_data.append(mld)

            file_manager.b_ml_opened = True

        except Exception as e:
            raise InputManagerException(
                error_id="mldat_read_error",
                error_description=f"Nie udało się odczytać pliku .mldat: {str(e)}"
            )

    def write(self, filepath: str, file_manager: "FileManager") -> None:
        """Zapisuje dane do pliku .mldat, filtrując adnotacje i zapobiegając duplikatom."""
        existing_records = []

        # 1. Odczytanie istniejących rekordów (aby nie nadpisać całości, a jedynie dodać/zaktualizować)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    existing_records = pickle.load(f)
            except Exception:
                pass  # Plik może być pusty lub uszkodzony

        # 2. Budowa słownika do szybkiego zapobiegania duplikatom
        # Kluczem jest unikalna kombinacja tych 4 wartości
        records_dict = {}
        for rec in existing_records:
            key = (rec['original_filename'], rec['signal_sample_index_start'], rec['signal_duration'],
                   rec['signal_name'])
            records_dict[key] = rec

        # Typy adnotacji do zignorowania
        ignored_types = [EAnnotationType.NORMAL_BEAT, EAnnotationType.EDF, EAnnotationType.UNKNOWN]

        # 3. Przetworzenie aktualnych danych ML i przypisanie adnotacji
        for mld in file_manager.machine_learning_data:
            extracted_annotations = []

            # Wyszukiwanie odpowiednich adnotacji
            for ann in file_manager.annotations:
                # Filtr 1: Pochodzenie EXTERNAL
                if getattr(ann, 'annotation_origin', None) != EAnnotationOrigin.EXTERNAL:
                    continue

                # Filtr 2: Ignorowane typy
                if ann.annotation_type in ignored_types:
                    continue

                # Filtr 3: Nazwa sygnału (jeśli jest przypisany do kanału)
                if ann.channel is not None and ann.channel != mld.signal_name:
                    continue

                # Filtr 4: Zasięg czasowy (sample_index wewnątrz okna transformaty)
                if mld.signal_sample_index_start <= ann.sample_index < (
                        mld.signal_sample_index_start + mld.signal_duration):
                    # Zapisujemy tylko typ i custom_label
                    extracted_annotations.append({
                        "annotation_type": ann.annotation_type.value,
                        "custom_label": ann.custom_label
                    })

            # Budowa struktury do zapisu (Twojego docelowego formatu)
            record = {
                "original_filename": mld.original_filename,
                "signal_sample_index_start": mld.signal_sample_index_start,
                "signal_duration": mld.signal_duration,
                "signal_name": mld.signal_name,
                "signal_fft": mld.signal_fft,
                "annotations": extracted_annotations
            }

            # Zapisanie do słownika - jeśli taki klucz już istniał, zostanie nadpisany
            key = (mld.original_filename, mld.signal_sample_index_start, mld.signal_duration, mld.signal_name)
            records_dict[key] = record

        # 4. Zrzut całości do pliku
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(list(records_dict.values()), f)
        except Exception as e:
            raise InputManagerException(
                error_id="mldat_save_error",
                error_description=f"Nie udało się zapisać pliku .mldat: {str(e)}"
            )