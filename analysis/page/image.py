import streamlit as st
from PIL import Image
from model.predict_image import detect_objects

def show_image_page():
    st.header("Phân Tích Ảnh Y Tế")

    uploaded_files = st.file_uploader("📤 Tải lên ảnh", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            image = Image.open(file)
            st.image(image, caption="Ảnh gốc", use_container_width=True)

            with st.spinner("🔍 Đang phân tích..."):
                result_img, detections = detect_objects(image)

            if result_img is not None:
                st.image(result_img, caption="🎯 Kết quả nhận dạng", use_container_width=True)

                st.markdown("### 🧾 Đối tượng phát hiện:")
                for label, conf in detections:
                    st.write(f"- **{label}** ({conf:.2%})")
            else:
                st.warning("⚠️ Không phát hiện đối tượng.")
