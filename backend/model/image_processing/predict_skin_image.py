# model/predict_skin.py

import numpy as np
import cv2
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# === Hàm khởi tạo model giống khi train ===
def build_model(num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# === Hàm dự đoán từ ảnh PIL.Image ===
from pathlib import Path

# Vị trí đúng của thư mục weights
WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights"

# Đường dẫn đầy đủ tới file model và label encoder
SKIN_WEIGHTS_PATH = WEIGHTS_DIR / "skin_disease.weights.h5"
SKIN_LABEL_ENCODER_PATH = WEIGHTS_DIR / "skin_label_encoder.pkl"

def predict_skin_disease(pil_image, weights_path= SKIN_WEIGHTS_PATH, label_path= SKIN_LABEL_ENCODER_PATH):
    # Đọc label encoder
    with open(label_path, "rb") as f:
        label_encoder = pickle.load(f)

    model = build_model(num_classes=len(label_encoder.classes_))
    model.load_weights(weights_path)

    img = pil_image.resize((128, 128)).convert("RGB")
    img_array = np.array(img, dtype=np.float32) / 255.0
    batch = np.expand_dims(img_array, 0)

    pred = model.predict(batch)[0]
    idx = np.argmax(pred)
    label = label_encoder.inverse_transform([idx])[0]
    confidence = float(pred[idx])
    return label, confidence
