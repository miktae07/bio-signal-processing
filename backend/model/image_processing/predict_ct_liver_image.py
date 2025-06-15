# model/predict_image.py
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
from tensorflow.keras.models import load_model
from typing import Tuple, List
import numpy as np
import time
from utils.utils import get_model_path

# Debug logger
def log_debug(msg):
    print(f"[DEBUG] {msg}")

# Determine directories relative to project root
def get_weights_dir():
    # This file is at: backend/model/predict_image.py
    # We want: backend/model/weights
    return Path(__file__).resolve().parent.parent / "weights"

WEIGHTS_DIR = get_weights_dir()
log_debug(f"Weights directory: {WEIGHTS_DIR}")

# Only the models needed
KERAS_MAP = {
    ("CT", "Liver"): WEIGHTS_DIR / "best_unet_resnet18_model.keras",
}
YOLO_CHEST_XRAY_PATH = WEIGHTS_DIR / "chest_xray.pt"

# Pre-load one YOLO model
YOLO_MODELS = {}
YOLO_KEY = ("X-Ray", "Chest")
try:
    start = time.time()
    log_debug(f"Loading YOLO model for {YOLO_KEY} from {YOLO_CHEST_XRAY_PATH}")
    YOLO_MODELS[YOLO_KEY] = YOLO(YOLO_CHEST_XRAY_PATH)
    log_debug(f"Loaded YOLO {YOLO_KEY} in {time.time()-start:.2f}s")
except Exception as e:
    log_debug(f"Failed to load YOLO model for {YOLO_KEY}: {e}")

# Pre-load Keras models globally
KERAS_MODELS = {}
for key, path in KERAS_MAP.items():
    model_path = get_model_path(str(path))
    try:
        start = time.time()
        log_debug(f"Loading Keras model for {key} from {model_path}")
        KERAS_MODELS[key] = load_model(model_path, compile=False)
        log_debug(f"Loaded Keras {key} in {time.time()-start:.2f}s")
    except Exception as e:
        log_debug(f"Failed to load Keras model for {key}: {e}")

# Expose model maps for use in other files
MODEL_MAP = {
    YOLO_KEY: YOLO_CHEST_XRAY_PATH
}


def detect_objects(model: YOLO, image: Image.Image) -> Tuple[np.ndarray, List[Tuple[str, float]]]:
    """Predict objects using a preloaded YOLO model."""
    start = time.time()
    results = model(image)
    log_debug(f"YOLO inference time: {time.time()-start:.2f}s")

    if not results or not hasattr(results[0], 'boxes'):
        return None, []

    result_img = results[0].plot()
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results[0].names[cls_id]
        detections.append((label, conf))
    return result_img, detections


def predict_ct_liver_mask(image: Image.Image, target_size=(128, 128), threshold=0.5) -> Image.Image:
    """Predict liver mask using a preloaded Keras model."""
    key = ("CT", "Liver")
    model = KERAS_MODELS.get(key)
    if model is None:
        raise ValueError(f"No Keras model found for key {key}")
    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")
    # Resize
    img_resized = image.resize(target_size)
    # Preprocess
    img_array = np.array(img_resized, dtype=np.float32) / 255.0
    batch = np.expand_dims(img_array, 0)
    # Predict with lower overhead
    start = time.time()
    pred = model.predict_on_batch(batch)[0]
    log_debug(f"Keras inference time: {time.time()-start:.2f}s")
    # Post-process
    mask = (pred > threshold).astype(np.uint8) * 255
    if mask.ndim == 3:
        mask = mask[..., 0]
    return Image.fromarray(mask)
