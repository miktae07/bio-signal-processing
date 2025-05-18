import streamlit as st
from PIL import Image
from tensorflow.keras.models import load_model as load_keras_model
from pathlib import Path
import numpy as np
from model.predict_image import model_loader, detect_objects, predict_ct_liver_mask

# Xác định thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "model" / "weights"
KERAS_DIR = BASE_DIR / "model" / "keras"

# Phân loại ảnh và bộ phận
IMAGE_TYPES = ["X-Ray", "MRI", "Ultrasound", "CT"]
BODY_PARTS_VI = {
    "Ngực": "Chest",
    "Não": "Brain",
    "Gan": "Liver",
    "Bụng": "Abdomen"
}

def show_image_page():
    st.header("🧠 Phân Tích Ảnh Y Tế")

    # 1. Chọn loại ảnh và bộ phận; mặc định CT Gan
    default_img_idx = IMAGE_TYPES.index("CT")
    default_part_idx = list(BODY_PARTS_VI.keys()).index("Gan")
    image_type = st.selectbox("🖼️ Chọn loại ảnh:", options=IMAGE_TYPES, index=default_img_idx)
    body_part_vi = st.selectbox("📍 Chọn bộ phận cơ thể:", options=list(BODY_PARTS_VI.keys()), index=default_part_idx)
    st.markdown(f"**🔍 Đang chọn:** {image_type} - {body_part_vi}")

    # 2. Load model tương ứng (trừ trường hợp MRI Não)
    if not (image_type == "MRI" and body_part_vi == "Não"):
        model, model_type = model_loader(image_type, body_part_vi)
        if model is None:
            st.error("❌ Không thể load mô hình.")
            return
    else:
        model, model_type = None, "pytorch"  # Sử dụng U-Net từ PyTorch cho MRI Não

    # 3. Upload ảnh
    uploaded_files = st.file_uploader(
        "📤 Tải lên ảnh (jpg/png)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )

    if not uploaded_files:
        return

    for file in uploaded_files:
        image = Image.open(file)
        
        # Chuyển ảnh thành numpy array
        img_array = np.array(image)
        
        # Kiểm tra và chuẩn bị ảnh cho MRI Não (cần 3 kênh)
        if image_type == "MRI" and body_part_vi == "Não":
            if img_array.ndim == 2:  # Ảnh grayscale
                img_array = np.stack([img_array] * 3, axis=-1)
            elif img_array.shape[-1] == 4:  # Xử lý ảnh RGBA
                img_array = img_array[:, :, :3]
            elif img_array.shape[-1] != 3:
                st.error("❌ Ảnh MRI cần có 3 kênh (RGB hoặc grayscale sẽ được chuyển đổi).")
                continue
            img_array = img_array.astype(np.float32)

        # Cột hiển thị song song
        col1, col2 = st.columns(2)

        # Cột 1: ảnh gốc
        with col1:
            st.image(image, caption="🖼️ Ảnh gốc", use_container_width=True)

        # Cột 2: ảnh kết quả
        with col2:
            with st.spinner("🔍 Đang phân tích..."):
                # Trường hợp đặc biệt: MRI - Não
                if image_type == "MRI" and body_part_vi == "Não":
                    st.warning("⚠️ Không phân tích được ảnh MRI.")
                    # result_img = detect_brain_abnormalities(img_array)
                    # if result_img is not None:
                    #     st.image(result_img, caption="🎯 Kết quả phân đoạn bất thường (đỏ)", use_container_width=True)
                    # else:
                    #     
                # Trường hợp đặc biệt: CT - Gan
                elif image_type == "CT" and body_part_vi == "Gan":
                    model_path = KERAS_DIR / "final_unet_resnet18_model.keras"
                    mask_img = predict_ct_liver_mask(str(model_path), image)
                    st.image(mask_img, caption="🎯 Kết quả phân đoạn Gan", use_container_width=True)

                # Trường hợp sử dụng mô hình Keras
                elif model_type == "keras":
                    img_array = np.array(image.resize((256, 256))) / 255.0
                    mask = model.predict(img_array[None, ...])[0]
                    mask_img = Image.fromarray((mask.squeeze() * 255).astype('uint8'))
                    st.image(mask_img, caption="🎯 Kết quả phân đoạn", use_container_width=True)

                # Trường hợp sử dụng mô hình khác (YOLO, v.v.)
                else:
                    result = detect_objects(model, image)
                    if isinstance(result, tuple):
                        result_img, detections = result
                    else:
                        result_img, detections = None, []

                    if result_img is not None:
                        st.image(result_img, caption="🎯 Kết quả nhận dạng", use_container_width=True)
                        st.markdown("### 🧾 Đối tượng phát hiện:")
                        for label, conf in detections:
                            st.write(f"- **{label}** ({conf:.2%})")
                    else:
                        st.warning("⚠️ Không phát hiện đối tượng hoặc lỗi khi phân tích.")