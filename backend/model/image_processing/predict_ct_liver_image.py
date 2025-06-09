# model/predict_image.py
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
from tensorflow.keras.models import load_model as keras_load
from typing import Tuple, List
import numpy as np
import tensorflow as tf
from utils.utils import get_model_path
from model.image_processing.predict_xray_chest_image import load_chexnet_model

# Xác định thư mục chứa weights
BASE_DIR = Path(__file__).resolve().parent.parent
print("Current working directory for image processing:", BASE_DIR)

WEIGHTS_DIR = BASE_DIR / "weights"
KERAS_DIR = BASE_DIR / "keras"

# Map hiển thị → key để chọn weights
BODY_PARTS_VI = {
    "Ngực": "Chest",
    "Não": "Brain",
    "Gan": "Liver",
    "Bụng": "Abdomen"
}

# PyTorch YOLOv8 weight map
MODEL_MAP = {
    ("X-Ray", "Chest"): WEIGHTS_DIR / "chest_xray.pt",
    ("MRI", "Brain"): WEIGHTS_DIR / "brain_mri.pt",
    ("Ultrasound", "Liver"): WEIGHTS_DIR / "ultrasound.pt",
    # default YOLOv8 nano
}

# Keras segmentation model map
KERAS_MAP = {
    ("CT", "Liver"): KERAS_DIR / "best_unet_resnet18_model.keras"
}

def detect_objects(
    model: object,
    image: Image.Image
) -> Tuple[Image.Image, List[Tuple[str, float]]]:
    """
    Dự đoán đối tượng trong ảnh với YOLO model.

    Args:
      model: YOLO instance
      image: PIL.Image

    Returns:
      result_img: numpy array có bounding boxes
      detections: list of (label, confidence)
    """
    results = model(image)
    if not results or len(results) == 0 or not hasattr(results[0], 'boxes'):
        return None, []

    result_img = results[0].plot()  # ảnh numpy với bounding boxes
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results[0].names[cls_id]
        detections.append((label, conf))

    return result_img, detections

def predict_ct_liver_mask(model_path: str, image: Image.Image) -> Image.Image:
    """
    Hàm dự đoán mask phân đoạn gan cho ảnh CT bằng mô hình đã huấn luyện.

    Args:
        model_path: đường dẫn file .keras đã lưu
        image: ảnh PIL.Image.Image đầu vào

    Returns:
        Ảnh PIL hiển thị mặt nạ đầu ra (grayscale)
    """
    model_path = get_model_path(model_path)
    model = keras_load(model_path)

    input_size = (128, 128)
    
    # ✅ Chuyển về RGB nếu ảnh có kênh Alpha hoặc Grayscale
    if image.mode != "RGB":
        image = image.convert("RGB")

    resized_image = image.resize(input_size)
    img_array = np.array(resized_image) / 255.0
    input_tensor = img_array[None, ...]  # shape (1, 128, 128, 3)

    pred_mask = model.predict(input_tensor)[0]  # shape (128, 128, 1)
    mask_img = Image.fromarray((pred_mask.squeeze() * 255).astype(np.uint8))

    return mask_img