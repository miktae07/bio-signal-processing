import streamlit as st
from utils.firebase_utils import get_sensor_groups
from utils.components import show_metrics, show_charts
from streamlit_autorefresh import st_autorefresh
from utils.utils import *

# Khởi tạo nhóm sensor
sensor_groups = get_sensor_groups()

def show_home_page():
    """
    Trang chủ hiển thị dữ liệu
    """
    st.image("assests/banner.jpg", use_container_width = True)
    st_autorefresh(interval= AUTO_REFRESH_INTERVAL_MS, key="auto_refresh")
    st.header("Trang Chủ – Hiển thị dữ liệu")
    
    # Nếu không có dữ liệu, thông báo lỗi
    if not sensor_groups:
        st.error("Chưa có dữ liệu từ Firebase!")
        return

    # Hiển thị header, metrics và biểu đồ real-time
    show_metrics(sensor_groups)
    show_charts(sensor_groups)


# Khi file được chạy độc lập để test, gọi hàm trực tiếp
if __name__ == "__main__":
    show_home_page()
