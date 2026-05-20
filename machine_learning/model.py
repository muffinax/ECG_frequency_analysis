import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from scipy.interpolate import interp1d
import numpy as np

from machine_learning.dataset_generator import folder_reader


def resample_complex_spectrum(freqs, fft, target_freqs):
    real_f = interp1d(freqs, np.real(fft), fill_value="extrapolate")
    imag_f = interp1d(freqs, np.imag(fft), fill_value="extrapolate")

    real_resampled = real_f(target_freqs)
    imag_resampled = imag_f(target_freqs)

    return real_resampled + 1j * imag_resampled

def model():
    # ------------------------
    # PARAMETRY
    # ------------------------
    time_steps = 100  # długość sekwencji (np. liczba okien FFT)
    num_features = 64  # liczba częstotliwości
    num_labels = 3  # liczba chorób

    # ------------------------
    # MODEL
    # ------------------------
    model = Sequential([

        # LSTM - analizuje sekwencję widm
        LSTM(128, return_sequences=True, input_shape=(time_steps, num_features)),
        BatchNormalization(),
        Dropout(0.3),

        LSTM(64),
        BatchNormalization(),
        Dropout(0.3),

        # warstwa gęsta
        Dense(32, activation='relu'),

        # 🔥 KLUCZ MULTILABEL
        Dense(num_labels, activation='sigmoid')
    ])

    # ------------------------
    # KOMPILACJA
    # ------------------------
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),

        # 🔥 KLUCZ MULTILABEL
        loss='binary_crossentropy',

        metrics=[
            tf.keras.metrics.Precision(),
            tf.keras.metrics.Recall()
        ]
    )

    model.summary()

def main():
    dataset = folder_reader("C:/Users/froma/OneDrive/Pulpit/mldata")

    for data in dataset:


if __name__ == "__main__":
    main()