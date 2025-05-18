# model/predict_image.py
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
from tensorflow.keras.models import load_model as keras_load
from typing import Tuple, List, Union, Dict
import numpy as np
import tensorflow as tf
# import torch
# import cv2

# Xác định thư mục chứa weights
BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "model" / "weights"
KERAS_DIR = BASE_DIR / "model" / "keras"

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

def model_loader(
    image_type: str,
    body_part_vi: str
) -> Tuple[object, str]:
    """
    Tự động load model segmentation (Keras) hoặc detection (YOLOv8) dựa vào loại ảnh và bộ phận.

    Args:
      image_type: one of ["X-Ray","MRI","Ultrasound","CT"]
      body_part_vi: key tiếng Việt trong BODY_PARTS_VI

    Returns:
      model: instance của Keras model hoặc YOLO
      model_type: "keras" hoặc "pt"
    """
    # dịch sang English key
    body_part_en = BODY_PARTS_VI.get(body_part_vi)
    if not body_part_en:
        raise ValueError(f"Unknown body part: {body_part_vi}")

    # 1) Thử Keras trước
    keras_path = KERAS_MAP.get((image_type, body_part_en))
    if keras_path and keras_path.exists():
        try:
            model = keras_load(str(keras_path))
            return model, "keras"
        except Exception as e:
            raise RuntimeError(f"Failed to load Keras model at {keras_path}: {e}")

    # 2) Nếu không thì dùng PyTorch YOLOv8
    pt_path = MODEL_MAP.get((image_type, body_part_en), WEIGHTS_DIR / "yolov8n.pt")
    if not pt_path.exists():
        raise FileNotFoundError(f"PyTorch model not found at {pt_path}")
    try:
        model = YOLO(str(pt_path))
        return model, "pt"
    except Exception as e:
        raise RuntimeError(f"Failed to load YOLO model at {pt_path}: {e}")

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
    model_path = "model/weights/best_unet_resnet18_model.keras"
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

# Danh sách 14 bệnh lý X-ray ngực 
LABELS = [
    'Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Infiltration',
    'Mass', 'Nodule', 'Atelectasis','Pneumothorax','Pleural_Thickening',
    'Pneumonia','Fibrosis','Edema','Consolidation'
]

def load_C3M3_model(model_weights_path: str) -> tf.keras.Model:
    """
    Tải model DenseNet121 multi-label (C3M3)
    """
    from keras.applications.densenet import DenseNet121
    from keras.models import Model
    from keras.layers import GlobalAveragePooling2D, Dense

    base = DenseNet121(include_top=False, input_shape=(320,320,3), weights=None)
    x = GlobalAveragePooling2D()(base.output)
    out = Dense(len(LABELS), activation='sigmoid')(x)
    model = Model(inputs=base.input, outputs=out)
    model.load_weights(model_weights_path)
    return model

def classify_chest_xray(
    image_input: Union[str, Image.Image],
    model: tf.keras.Model,
    input_size: tuple = (320, 320)
) -> Dict[str, float]:
    """
    Multi-label classification trên Chest X-ray với C3M3.

    Args:
        image_input: đường dẫn tới file ảnh hoặc PIL.Image.
        model: instance của C3M3 (DenseNet121-based) đã load weights.
        input_size: kích thước resize (height, width), mặc định (320, 320).

    Returns:
        Dict[nhãn → xác suất (0–1)] cho 14 bệnh lý.
    """
    # 1. Load & convert
    if isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        img = image_input

    # 2. Chuyển về RGB & resize
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize(input_size)

    # 3. To array và chuẩn hóa
    x = keras_image.img_to_array(img)  # float32, [0,255]
    x = x / 255.0                       # scale về [0,1]
    x = np.expand_dims(x, axis=0)       # shape (1, H, W, 3)

    # 4. Dự đoán
    preds = model.predict(x)[0]         # 14-dim array

    # 5. Map về dict
    return {label: float(preds[i]) for i, label in enumerate(LABELS)}


# def detect_brain_abnormalities(mri_image):
#     """
#     Phát hiện các bất thường trong ảnh MRI não và trả về ảnh có các bất thường được làm nổi bật.
    
#     :param mri_image: Ảnh MRI não dưới dạng numpy array với shape (H, W, 3), 
#                       trong đó H và W là chiều cao và chiều rộng, và 3 là số kênh (pre-contrast, FLAIR, post-contrast).
#     :return: Ảnh kết quả dưới dạng numpy array với shape (H, W, 3), uint8, có các bất thường được làm nổi bật bằng màu đỏ.
#     """
    
#     # Bước 1: Load mô hình U-Net đã huấn luyện sẵn
#     model = torch.hub.load('mateuszbuda/brain-segmentation-pytorch', 'unet', in_channels=3, out_channels=1, init_features=32, pretrained=True)
#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#     model = model.to(device)
    
#     # Bước 2: Lưu trữ kích thước gốc của ảnh
#     H, W, _ = mri_image.shape
    
#     # Bước 3: Resize ảnh về kích thước 256x256 (kích thước yêu cầu của mô hình)
#     mri_resized = cv2.resize(mri_image, (256, 256), interpolation=cv2.INTER_LINEAR)
    
#     # Bước 4: Chuẩn hóa ảnh (z-score normalization per channel)
#     mri_normalized = np.zeros_like(mri_resized)
#     for c in range(3):
#         channel = mri_resized[:, :, c]
#         mean = np.mean(channel)
#         std = np.std(channel)
#         if std > 0:
#             mri_normalized[:, :, c] = (channel - mean) / std
#         else:
#             mri_normalized[:, :, c] = 0  # Tránh chia cho không
    
#     # Bước 5: Chuyển đổi ảnh thành tensor và di chuyển lên GPU nếu có
#     input_tensor = torch.from_numpy(mri_normalized).permute(2, 0, 1).float().unsqueeze(0).to(device)
    
#     # Bước 6: Dự đoán bằng mô hình
#     with torch.no_grad():
#         output = model(input_tensor)
    
#     # Bước 7: Chuyển đổi output thành numpy array và áp dụng ngưỡng (threshold) để lấy mask nhị phân
#     mask = (output.squeeze().cpu().numpy() > 0.5).astype(int)  # Shape: (256, 256)
    
#     # Bước 8: Resize mask về kích thước gốc của ảnh
#     mask_resized = cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)
    
#     # Bước 9: Chuẩn bị ảnh gốc để hiển thị (chỉ lấy kênh đầu tiên và scale về [0, 255])
#     first_channel = mri_image[:, :, 0]
#     min_val = np.min(first_channel)
#     max_val = np.max(first_channel)
#     if max_val > min_val:
#         displayed = (first_channel - min_val) / (max_val - min_val) * 255
#     else:
#         displayed = np.zeros_like(first_channel)
#     displayed = displayed.astype(np.uint8)
    
#     # Bước 10: Tạo ảnh RGB từ ảnh grayscale
#     rgb = np.stack([displayed, displayed, displayed], axis=2)
    
#     # Bước 11: Làm nổi bật các bất thường bằng màu đỏ
#     rgb[mask_resized == 1] = np.array([255, 0, 0])
    
#     return rgb