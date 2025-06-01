import streamlit as st
from utils.firebase_utils import get_sensor_groups, create_user_profile
from utils.components import show_metrics, show_charts
from streamlit_autorefresh import st_autorefresh
from utils.utils import *
from utils.firebase_utils import (
    get_sensor_groups,
)

# Custom CSS để tối ưu khoảng cách
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

def show_home_page():
    """
    Trang chủ hiển thị dữ liệu, cho phép tạo user mới, có nút làm mới dữ liệu thủ công,
    hiển thị thông tin hồ sơ cá nhân, và có nút đăng xuất.
    """
    st_autorefresh(interval=AUTO_REFRESH_INTERVAL_MS, key="auto_refresh")
    st.header("🏠 Trang Chủ – Hiển Thị Dữ Liệu")

    # === NÚT LÀM MỚI DỮ LIỆU ===
    if st.button("Reload Data"):
        st.session_state["reload_data"] = True

    # === LẤY DỮ LIỆU SENSOR ===
    if st.session_state.get("reload_data", False):
        sensor_groups = get_sensor_groups()
        st.session_state["sensor_groups"] = sensor_groups
        st.session_state["reload_data"] = False
    else:
        sensor_groups = st.session_state.get("sensor_groups", get_sensor_groups())
        st.session_state["sensor_groups"] = sensor_groups

    # === HIỂN THỊ SỐ LIỆU SENSOR ===
    if not sensor_groups:
        st.error("⚠️ Chưa có dữ liệu từ Firebase!")
    else:
        show_metrics(sensor_groups)
        show_charts(sensor_groups)

