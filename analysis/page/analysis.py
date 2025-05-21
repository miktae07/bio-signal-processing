import streamlit as st
import pandas as pd
from datetime import datetime, time
from utils.utils import map_vietnamese_to_english
from utils.firebase_utils import get_sensor_groups
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
    available_signals = [k for k, v in name_to_key.items() if v in sensor_groups]
    selected = st.multiselect(
        "Chọn tín hiệu phân tích",
        options=available_signals,
        default=available_signals
    )

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

        export_data = []
        summary_rows = []

        if 'BPM' in selected:
            df_bpm = sensor_groups[name_to_key['BPM']].copy()
            if 'value' not in df_bpm.columns:
                st.error("❌ Dữ liệu BPM không chứa cột 'value'. Vui lòng kiểm tra dữ liệu.")
                return
            df_bpm = df_bpm[(df_bpm.index >= start_dt) & (df_bpm.index <= end_dt)]
            bpm_stats, bpm_status = analyze_bpm_window(df_bpm, start_dt, end_dt)
            bpm_status_en = map_vietnamese_to_english(bpm_status)

            st.subheader("📈 Kết quả BPM")
            st.write(f"- Trung bình: {bpm_stats['mean']:.1f} bpm")
            st.write(f"- Min: {bpm_stats['min']:.1f} bpm")
            st.write(f"- Max: {bpm_stats['max']:.1f} bpm")
            st.write(f"- Trạng thái: **{bpm_status}**")

            for idx, row in df_bpm.iterrows():
                export_data.append([
                    'BPM', idx, row['value'], bpm_status_en
                ])

            summary_rows.append(["BPM", bpm_stats['min'], bpm_stats['max'], bpm_stats['mean'], bpm_status_en])

        if 'SpO₂' in selected:
            df_spo2 = sensor_groups[name_to_key['SpO₂']].copy()
            if 'value' not in df_spo2.columns:
                st.error("❌ Dữ liệu SpO₂ không chứa cột 'value'. Vui lòng kiểm tra dữ liệu.")
                return
            df_spo2 = df_spo2[(df_spo2.index >= start_dt) & (df_spo2.index <= end_dt)]
            spo2_stats, spo2_status = analyze_spo2_window(df_spo2, start_dt, end_dt)
            spo2_status_en = map_vietnamese_to_english(spo2_status)

            st.subheader("📈 Kết quả SpO₂")
            st.write(f"- Trung bình: {spo2_stats['mean']:.1f}%")
            st.write(f"- Min: {spo2_stats['min']:.1f}%")
            st.write(f"- Max: {spo2_stats['max']:.1f}%")
            st.write(f"- Trạng thái: **{spo2_status}**")

            for idx, row in df_spo2.iterrows():
                export_data.append([
                    'SpO2', idx, row['value'], spo2_status_en
                ])

            summary_rows.append(["SpO2", spo2_stats['min'], spo2_stats['max'], spo2_stats['mean'], spo2_status_en])

        
        if export_data:
            # Tạo DataFrame để export, bỏ cột index
            df_export = pd.DataFrame(export_data, columns=["Data Type", "Timestamp", "Value", "Analysis Result"])
            st.download_button(
                label="📥 Tải về CSV",
                data=df_export.to_csv(index=False, encoding='utf-8-sig'),
                file_name="ket_qua_phan_tich.csv",
                mime="text/csv"
            )
            st.dataframe(df_export)

        if summary_rows:
            df_summary = pd.DataFrame(summary_rows, columns=["Data Type", "Min", "Max", "Mean", "Analysis Result"])
            st.subheader("📊 Tổng hợp theo loại dữ liệu")
            st.dataframe(df_summary)

        if len(summary_rows) == 2:
            overall = evaluate_health(bpm_stats, bpm_status, spo2_stats, spo2_status)
            st.subheader("🩺 Đánh giá tổng quát")
            st.write(f"- Kết luận chung: **{overall}**")
