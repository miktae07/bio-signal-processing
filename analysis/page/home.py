import streamlit as st
from utils.firebase_utils import get_sensor_groups
from utils.components import show_metrics, show_charts, show_profile
from streamlit_autorefresh import st_autorefresh
from utils.utils import *

st.markdown(
    """
    <style>
        .block-container {
            margin-top: 0rem !important;
            padding-top: 0rem !important;
        }
        .css-18e3th9 {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        header {
            margin-bottom: 0rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Khởi tạo nhóm sensor
sensor_groups = get_sensor_groups()

def show_home_page():
    """
    Trang chủ hiển thị dữ liệu
    """
    st_autorefresh(interval= AUTO_REFRESH_INTERVAL_MS, key="auto_refresh")
    st.header("Trang Chủ – Hiển thị dữ liệu")

    col1, col_mid, col2 = st.columns([1, 0.02, 3], gap="small")

    with col1:
        # Thay dưới đây bằng dữ liệu thực của bạn
        user_name = "Nguyễn Văn A"
        user_age = 28
        user_address = "123 Đường Lê Lợi, Hà Nội"
        user_gender = "Nam"
        show_profile(user_name, user_age, user_address, user_gender)
    with col_mid:
        st.markdown(
            """
            <div style="
                border-left: 1px solid #000;
                height: 100%;
                margin: 0px 0px;
            "></div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        if not sensor_groups:
            st.error("Chưa có dữ liệu từ Firebase!")
        else:
            show_metrics(sensor_groups)
            show_charts(sensor_groups)

# Khi file được chạy độc lập để test, gọi hàm trực tiếp
if __name__ == "__main__":
    show_home_page()
