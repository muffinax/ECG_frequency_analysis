import tkinter as tk
from tkinter import filedialog


"""
Na dole - Bytner importy - Python 3.11
"""
import tensorflow as tf

Sequential = tf.keras.models.Sequential
Dense = tf.keras.layers.Dense
Dropout = tf.keras.layers.Dropout
Conv1D = tf.keras.layers.Conv1D
Flatten = tf.keras.layers.Flatten
BatchNormalization = tf.keras.layers.BatchNormalization

from sklearn.model_selection import train_test_split
from scipy.interpolate import interp1d

import numpy as np

from machine_learning.dataset_generator import folder_reader


""" 
!!!!!! UWAGA !!!! 

Importy wyżej mogą być błędne zależnie od tego jakie środowisko i jaki interpreter używacie
Zamiast wymieniać sie i zmieniac importy, prośze "błędne" dla was komentować i dawać swoje "I najlepiej jak napiszecie jaka wersja i czyje
Dzięki 
"""



LABEL_MAP = {
    "+": 0,
    "/": 1,
    "L": 2,
    "R": 3,
    "V": 4,
    "~": 5

}

NUM_LABELS = 6


def wybierz_folder():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(
        title="Wybierz folder z danymi ML"
    )

    root.destroy()

    if not folder_path:
        print("Nie wybrano folderu.")
        return None

    print("Wybrany folder:", folder_path)

    return folder_path


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


def annotations_to_vector(annotations):
    y = np.zeros(NUM_LABELS, dtype=np.float32)

    for ann in annotations:
        label = ann["annotation_type"]

        if label in LABEL_MAP:
            idx = LABEL_MAP[label]
            y[idx] = 1.0

    return y

def resample_complex_spectrum(freqs, fft, target_freqs):
    real_f = interp1d(freqs, np.real(fft), fill_value="extrapolate")
    imag_f = interp1d(freqs, np.imag(fft), fill_value="extrapolate")

    real_resampled = real_f(target_freqs)
    imag_resampled = imag_f(target_freqs)

    return real_resampled + 1j * imag_resampled


def reduce_negative_samples(x, y, reduction_percent=0.8, random_state=42):
    """
    Usuwa część próbek negatywnych.

    reduction_percent=0.8:
    - usuwa 80% próbek bez etykiet
    - zostawia 20% próbek bez etykiet
    """

    rng = np.random.default_rng(random_state)

    positive_mask = np.sum(y, axis=1) > 0
    negative_mask = np.sum(y, axis=1) == 0

    x_positive = x[positive_mask]
    y_positive = y[positive_mask]

    x_negative = x[negative_mask]
    y_negative = y[negative_mask]

    negative_count = len(x_negative)

    keep_negative_count = int(
        negative_count * (1.0 - reduction_percent)
    )

    selected_negative_indices = rng.choice(
        negative_count,
        size=keep_negative_count,
        replace=False
    )

    x_negative_reduced = x_negative[selected_negative_indices]
    y_negative_reduced = y_negative[selected_negative_indices]

    x_reduced = np.concatenate(
        [x_positive, x_negative_reduced],
        axis=0
    )

    y_reduced = np.concatenate(
        [y_positive, y_negative_reduced],
        axis=0
    )

    shuffle_indices = rng.permutation(len(x_reduced))

    x_reduced = x_reduced[shuffle_indices]
    y_reduced = y_reduced[shuffle_indices]

    return x_reduced, y_reduced


def model():
    model = Sequential([
        Conv1D(64, 3, activation="relu", input_shape=(128, 2)),
        BatchNormalization(),

        Conv1D(128, 3, activation="relu"),
        BatchNormalization(),
        Dropout(0.3),

        Flatten(),

        Dense(64, activation="relu"),
        Dense(NUM_LABELS, activation="sigmoid")
    ])

    model.compile(
        optimizer="adam",
        loss=focal_loss(alpha=0.25, gamma=2.0),
        metrics=[
            tf.keras.metrics.AUC(curve="PR"),
            tf.keras.metrics.Precision(),
            tf.keras.metrics.Recall()
        ]
    )

    return model

def build_dataset(dataset):
    target_freqs = np.linspace(0, 180, 128)

    x = []
    y = []

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

        y.append(annotations_to_vector(data.annotations))

    return np.array(x), np.array(y)


def main():

    folder_path = wybierz_folder()

    if folder_path is None:
        return

    dataset = folder_reader(folder_path)

    print("Dataset length:", len(dataset))

    x, y = build_dataset(dataset)

    print("\nPRZED REDUKCJĄ:")
    print("Liczba etykiet pozytywnych na klasę:",
          np.sum(y, axis=0))
    print("Liczba próbek bez żadnej etykiety:",
          np.sum(np.sum(y, axis=1) == 0))

    x = np.array(x)
    y = np.array(y)

    print("x shape przed redukcją:", x.shape)
    print("y shape przed redukcją:", y.shape)

    # ------------------------
    # REDUKCJA NEGATYWNYCH
    # ------------------------

    x, y = reduce_negative_samples(
        x,
        y,
        reduction_percent=0.995
    )

    print("\nPO REDUKCJI:")
    print("Liczba etykiet pozytywnych na klasę:",
          np.sum(y, axis=0))
    print("Liczba próbek bez żadnej etykiety:",
          np.sum(np.sum(y, axis=1) == 0))

    print("Przykładowe y po redukcji:")
    print(y[:10])

    print("x shape po redukcji:", x.shape)
    print("y shape po redukcji:", y.shape)

    # ------------------------
    # TRAIN / TEST SPLIT
    # ------------------------

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=np.any(y == 1, axis=1)
    )

    # ------------------------
    # MODEL
    # ------------------------

    m = model()

    history = m.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        epochs=20,
        batch_size=32
    )

    # ------------------------
    # PREDYKCJA
    # ------------------------

    y_pred = m.predict(x_test)

    y_pred_bin = predict_threshold(y_pred, t=0.2)

    print("\nPREDYKCJE:")
    print("mean prediction:", np.mean(y_pred))
    print("max prediction:", np.max(y_pred))
    print("sample preds:", y_pred[:3])

    # ------------------------
    # EWALUACJA
    # ------------------------

    results = m.evaluate(x_test, y_test)

    print("\nTest results:", results)

    # ------------------------
    # ZAPIS MODELU
    # ------------------------

    m.save("ecg_model.keras")

    print("\nModel zapisany jako ecg_model.keras")


if __name__ == "__main__":
    main()