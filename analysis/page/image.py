import streamlit as st
from PIL import Image
import torch
from pathlib import Path

# Thư viện model
from model.image_processing.predict_ct_liver_image import predict_ct_liver_mask, detect_objects
from model.image_processing.predict_xray_chest_image import load_chexnet_model, predict_chexnet
from ultralytics import YOLO

# Thiết lập đường dẫn
BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "model"/ "weights"

# Các tuỳ chọn
IMAGE_TYPES = ["X-Ray", "MRI", "Ultrasound", "CT"]
BODY_PARTS = {"Ngực":"Chest","Não":"Brain","Gan":"Liver","Bụng":"Abdomen"}

# Helper để load YOLO
def load_yolo(image_type, part_en):
    pt = (WEIGHTS_DIR / f"{part_en.lower()}_xray.pt") if image_type=="X-Ray" else WEIGHTS_DIR / "yolov8n.pt"
    return YOLO(str(pt))

# Trang chính
def show_image_page():
    st.header("🧠 Phân Tích Ảnh Y Tế")
    img_type = st.selectbox("Chọn loại ảnh", IMAGE_TYPES, index=3)
    part_vi = st.selectbox("Chọn bộ phận", list(BODY_PARTS), index=2)
    st.write(f"**Bạn chọn:** {img_type} - {part_vi}")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    files = st.file_uploader("Tải ảnh (jpg/png)", type=["jpg","png"], accept_multiple_files=True)
    if not files: return

    for f in files:
        img = Image.open(f)
        col1, col2 = st.columns(2)
        with col1: st.image(img, caption="Ảnh gốc", use_container_width=True)
        with col2:
            st.spinner("Đang xử lý...")
            part_en = BODY_PARTS[part_vi]
            if img_type=="X-Ray" and part_vi=="Ngực":
                model = load_chexnet_model(str(WEIGHTS_DIR/"chexnet_weights.pth.tar"), device)
                result = predict_chexnet(model, img, device)
                st.image(result, caption="Kết quả X-Ray", use_container_width=True)
            elif img_type=="CT" and part_vi=="Gan":
                result = predict_ct_liver_mask(str(WEIGHTS_DIR/"best_unet_resnet18_model.keras"), img)
                st.image(result, caption="Kết quả CT Gan", use_container_width=True)
            elif img_type!="MRI":
                yolo = load_yolo(img_type, part_en)
                img_out, det = detect_objects(yolo, img)
                if img_out: st.image(img_out, caption="Kết quả detection", use_container_width=True)
            else:
                st.warning("Không hỗ trợ MRI Não")
