import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Conv1D, Flatten
from scipy.interpolate import interp1d

import numpy as np

from machine_learning.dataset_generator import folder_reader

LABEL_MAP = {
    "+": 0,
    "/": 1,
    "L": 2,
    "R": 3,
    "V": 4
}
NUM_LABELS = 5

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
        fft_resampled = resample_complex_spectrum(data.signal_fft_freqs, data.signal_fft, target_freqs)

        features = np.stack([np.real(fft_resampled), np.imag(fft_resampled)], axis=-1)

        x.append(features)

        y.append(annotations_to_vector(data.annotations))

    return np.array(x), np.array(y)

def main():
    dataset = folder_reader("C:/Users/froma/OneDrive/Pulpit/mldata")

    x, y = build_dataset(dataset)

    x = np.array(x)
    y = np.array(y)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify = np.any(y == 1, axis=1))

    m = model()

    history = m.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=20, batch_size=32)

    y_pred = m.predict(x_test)

    y_pred_bin = predict_threshold(y_pred, t=0.2)

    print("mean prediction:", np.mean(y_pred))
    print("max prediction:", np.max(y_pred))
    print("sample preds:", y_pred[:3])

    results = m.evaluate(x_test, y_test)

    print("Test results:", results)

    m.save("ecg_model.keras")

if __name__ == "__main__":
    main()