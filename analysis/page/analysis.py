import streamlit as st
import altair as alt
import pandas as pd
from utils.firebase_utils import get_sensor_groups
from datetime import datetime, time
from model.analyse import analyze_bpm_window, analyze_spo2_window, evaluate_health


def show_analysis_page():
    """
    Trang phân tích dữ liệu cảm biến BPM & SpO₂ sử dụng các hàm phân tích riêng.
    """
    st.header("Phân Tích Dữ Liệu Y Tế")

    # Lấy dữ liệu từ Firebase
    sensor_groups = get_sensor_groups()
    if not sensor_groups:
        st.warning("⚠️ Không tìm thấy dữ liệu để phân tích.")
        return

    # Map tên hiển thị → key thực trong sensor_groups
    name_to_key = {
        'BPM': 'BPM',
        'SpO₂': 'SpO2'  # SpO2 là key thực tế lấy từ Firebase
    }

    # Chọn tín hiệu để phân tích
    # st.write("🧪 Sensor Groups:", list(sensor_groups.keys()))
    available_signals = [k for k, v in name_to_key.items() if v in sensor_groups]
    selected = st.multiselect(
        "Chọn tín hiệu phân tích",
        options=available_signals,
        default=available_signals
    )

    # ✅ Hiển thị lựa chọn đang được chọn
    # st.write("✅ Bạn đã chọn:", selected)

    # Chọn khoảng ngày giờ
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Ngày bắt đầu", value=pd.to_datetime("2025-01-01"))
        start_time = st.time_input("Giờ bắt đầu", value=time(0, 0))
    with col2:
        end_date = st.date_input("Ngày kết thúc", value=pd.to_datetime("2025-12-31"))
        end_time = st.time_input("Giờ kết thúc", value=time(23, 59, 59))

    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)

    if st.button("🔍 Chạy phân tích"):
        if start_dt > end_dt:
            st.error("⚠️ Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc.")
            return

        bpm_stats = bpm_status = spo2_stats = spo2_status = None

        if 'BPM' in selected:
            df_bpm = sensor_groups[name_to_key['BPM']].copy()
            bpm_stats, bpm_status = analyze_bpm_window(df_bpm, start_dt, end_dt)
            st.subheader("📈 Kết quả BPM")
            st.write(f"- Trung bình: {bpm_stats['mean']:.1f} bpm")
            st.write(f"- Min: {bpm_stats['min']:.1f} bpm")
            st.write(f"- Max: {bpm_stats['max']:.1f} bpm")
            st.write(f"- Trạng thái: **{bpm_status}**")

        if 'SpO₂' in selected:
            df_spo2 = sensor_groups[name_to_key['SpO₂']].copy()
            spo2_stats, spo2_status = analyze_spo2_window(df_spo2, start_dt, end_dt)
            st.subheader("📈 Kết quả SpO₂")
            st.write(f"- Trung bình: {spo2_stats['mean']:.1f}%")
            st.write(f"- Min: {spo2_stats['min']:.1f}%")
            st.write(f"- Max: {spo2_stats['max']:.1f}%")
            st.write(f"- Trạng thái: **{spo2_status}**")

        if all([bpm_stats, bpm_status, spo2_stats, spo2_status]):
            overall = evaluate_health(bpm_stats, bpm_status, spo2_stats, spo2_status)
            st.subheader("📊 Đánh giá tổng quát")
            st.write(f"- Kết luận chung: **{overall}**")
