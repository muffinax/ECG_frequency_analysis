from pathlib import Path
import tensorflow as tf
import numpy as np
from scipy.interpolate import interp1d

from ai_api.dataset_generator import folder_reader
from file_manager import FileManager, Annotation, EAnnotationOrigin, EAnnotationType

LABEL_MAP = {
    "+": 0,
    "/": 1,
    "L": 2,
    "R": 3,
    "V": 4,
    "~": 5
}

IDX_TO_ANNOTATION = {
    0: EAnnotationType.RHYTHM_CHANGE, # "+"
    1: EAnnotationType.PACED_BEAT,  # "/"
    2: EAnnotationType.LEFT_BUNDLE_BRANCH_BLOCK,  # "L"
    3: EAnnotationType.RIGHT_BUNDLE_BRANCH_BLOCK,  # "R"
    4: EAnnotationType.PREMATURE_VENTRICULAR_CONTRACTION,  # "V"
    5: EAnnotationType.CHANGE_IN_SIGNAL_QUALITY,  # "~"
}

NUM_LABELS = 6

def focal_loss(alpha=0.25, gamma=2.0):
    def loss(y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1 - 1e-7)
        pt = tf.where(tf.equal(y_true, 1), y_pred, 1 - y_pred)
        return -tf.reduce_mean(
            alpha * tf.pow(1 - pt, gamma) * tf.math.log(pt)
        )
    return loss

def predict_threshold(y_pred, t=0.2):
    return (y_pred > t).astype(int)

def resample_complex_spectrum(freqs, fft, target_freqs):
    real_f = interp1d(freqs, np.real(fft), fill_value="extrapolate")
    imag_f = interp1d(freqs, np.imag(fft), fill_value="extrapolate")

    real_resampled = real_f(target_freqs)
    imag_resampled = imag_f(target_freqs)

    return real_resampled + 1j * imag_resampled

def build_dataset(dataset):
    target_freqs = np.linspace(0, 180, 128)

    x = []

    for data in dataset:
        fft_resampled = resample_complex_spectrum(data.signal_fft_freqs, data.signal_fft, target_freqs)

        features = np.stack([np.real(fft_resampled), np.imag(fft_resampled)], axis=-1)

        x.append(features)

    return np.array(x)

def load_keras_model():
    base_dir = Path(__file__).resolve().parent
    model_dir = base_dir.parent / "model"

    model_files = list(model_dir.glob("*.keras"))

    if not model_files:
        raise FileNotFoundError("Brak modelu .keras w folderze model")

    model_path = max(model_files, key=lambda p: p.stat().st_mtime)

    return tf.keras.models.load_model(
        model_path,
        custom_objects={"loss": focal_loss()}
    )

def preprocess_for_model(dataset):
    target_freqs = np.linspace(0, 180, 128)
    x = []

    for data in dataset:
        fft_resampled = resample_complex_spectrum(
            data.signal_fft_freqs,
            data.signal_fft,
            target_freqs
        )

        features = np.stack(
            [np.real(fft_resampled), np.imag(fft_resampled)],
            axis=-1
        )

        x.append(features)

    return np.array(x)

def predictions_to_annotations(y_pred, dataset, file_manager, threshold=0.2):
    annotations = []

    for i, data in enumerate(dataset):
        probs = y_pred[i]
        start_t = int(data.signal_sample_index_start * file_manager.sampling_frequency)
        duration = int(data.signal_duration * file_manager.sampling_frequency)

        for class_idx, p in enumerate(probs):

            if p < threshold:
                continue

            annotation_type = IDX_TO_ANNOTATION.get(class_idx)

            annotations.append(
                Annotation(
                    sample_index=start_t,
                    annotation_duration=duration,

                    annotation_origin=EAnnotationOrigin.ANALYSIS,

                    annotation_type=annotation_type,

                    auxiliary_note=f"conf={p:.3f}",

                    channel=data.signal_name
                )
            )

    return annotations

def use_model(dataset, file_manager):
    model = load_keras_model()

    x = preprocess_for_model(dataset)

    pred = model.predict(x)

    annotations = predictions_to_annotations(pred, dataset, file_manager)

    return annotations