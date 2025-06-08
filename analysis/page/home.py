import streamlit as st
from utils.firebase_utils import get_sensor_groups
from utils.update_data import start_sensor_listener
from utils.utils import AUTO_REFRESH_INTERVAL_MS
from utils.components import show_metrics, show_charts
import pandas as pd

def load_sensor_groups():
    return get_sensor_groups()

def update_ui_on_change(sensor, df):
    print(f"🔄 Đã cập nhật từ cảm biến: {sensor}")
    print(df.tail(1))

    if df.index.dtype != 'datetime64[ns]':
        df.index = pd.to_datetime(df.index)

    if 'sensor_groups' not in st.session_state:
        st.session_state['sensor_groups'] = {}

    st.session_state['sensor_groups'][sensor] = df

    print("✅ Session state sau cập nhật:")
    print(st.session_state['sensor_groups'][sensor].tail())

    st.session_state["need_rerun"] = True
    print("[update_ui_on_change] ➕ Ghi buffer và set need_rerun = True")


def show_home_page():
    if st.session_state.get("need_rerun"):
        print("[show_home_page] 🔄 Có cờ need_rerun = True → sẽ cập nhật giao diện")
        st.session_state["need_rerun"] = False
        st.rerun()
        sensor_groups = st.session_state.get('sensor_groups', {})
        if not sensor_groups:
            st.error("⚠️ Chưa có dữ liệu từ Firebase!")
        else:
            # Hiển thị các chỉ số và biểu đồ
            show_metrics(sensor_groups)
            show_charts(sensor_groups)

    st.header("🏠 Trang Chủ – Hiển Thị Dữ Liệu")

    # Lấy snapshot ban đầu
    st.session_state['sensor_groups'] = get_sensor_groups()
    # Bắt listener
    st.session_state['fb_listener'] = start_sensor_listener(
        on_change=update_ui_on_change,
        debug=True
    )
    
    # 2) Nút reload dữ liệu thủ công
    if st.button("Reload Data"):
        st.session_state['sensor_groups'] = get_sensor_groups()
        st.rerun()
    
    sensor_groups = st.session_state.get('sensor_groups', {})
    if not sensor_groups:
        st.error("⚠️ Chưa có dữ liệu từ Firebase!")
    else:
        # Hiển thị các chỉ số và biểu đồ
        show_metrics(sensor_groups)
        show_charts(sensor_groups)

show_home_page()