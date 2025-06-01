import streamlit as st
import altair as alt
from model.analyse import *
from datetime import timedelta
from model.data_processing.bpm_analyse import analyze_bpm_window
from model.data_processing.spo2_analyse import analyze_spo2_window
from model.data_processing.ecg_analyse import analyze_ecg_window

def get_unit(sensor):
    """Trả về đơn vị của cảm biến nếu có"""
    if sensor.upper() == "BPM":
        return "bpm"
    elif sensor.upper() == "SPO2":
        return "%"
    elif sensor.upper() == "EEG":
        return "µV"
    else:
        return ""
    
def get_sensor_icon(sensor):
    sensor = sensor.upper()
    if "BPM" in sensor or "HEART" in sensor:
        return "❤️"  # Nhịp tim
    elif "SPO2" in sensor or "OXY" in sensor:
        return "🫁"  # Nồng độ oxy
    elif "EEG" in sensor:
        return "🧠"  # Sóng não
    elif "ECG" in sensor:
        return "🫀"  # Điện tim
    elif "TEMP" in sensor or "NHIỆT" in sensor:
        return "🌡️"  # Nhiệt độ
    elif "HUM" in sensor or "ĐỘ ẨM" in sensor:
        return "💧"  # Độ ẩm
    else:
        return "🔧"  # Mặc định

def show_metrics(sensor_groups):
    st.markdown("## 📊 Dữ liệu Hiện Tại")

    with st.container():
        cols = st.columns(len(sensor_groups))

        for i, (sensor, df) in enumerate(sensor_groups.items()):
            print(f"Processing {sensor}...")
            with cols[i]:
                # 📌 1. Thông tin cơ bản
                value = df['value'].iloc[-1]
                timestamp = df.index[-1]
                unit = get_unit(sensor)
                icon = get_sensor_icon(sensor)
                display_label = f"{icon} {sensor}"
                display_value = f"{value:.2f} {unit}" if unit else f"{value:.2f}"

                # 🟩 2. Hiển thị số liệu
                st.metric(label=display_label, value=display_value, delta=None, border=True)

                # 🕒 3. Hiển thị 
                st.markdown(
                    f"<div style='margin-top: -10px; font-size: 14px; color: #555;'>🕒 <strong>{timestamp.strftime('%d-%m-%Y %H:%M:%S')}</strong></div>",
                    unsafe_allow_html=True
                )

                # 🩺 4. Phân tích trạng thái trên 5 phút dữ liệu cuối
                end_time = df.index.max()
                start_time = end_time - timedelta(minutes=5)
                window_df = df[(df.index >= start_time) & (df.index <= end_time)]

                status = "Không xác định"
                confidence_text = ""
                try:
                    if "BPM" in sensor.upper():
                        _, bpm_status = analyze_bpm_window(window_df, start_time, end_time)
                        status = bpm_status
                    elif "SPO2" in sensor.upper():
                        _, spo2_status = analyze_spo2_window(window_df, start_time, end_time)
                        status = spo2_status
                    elif "ECG" in sensor.upper():
                        print("Analyzing ECG window...")
                        _, class_name, confidence = analyze_ecg_window(window_df, start_time, end_time)
                        status = class_name
                        confidence_pct = confidence * 100
                        confidence_text = f"{confidence_pct:.1f}%"
                    else:
                        status = "Không xác định"
                        confidence_text = ""
                except Exception as e:
                    status = f"Lỗi: {str(e)}"
                    confidence_text = ""

                # ✅ 5. Hiển thị trạng thái
                color = "green" if "bình thường" in status.lower() else "red"
                if confidence_text:
                    st.markdown(
                        f"<div style='font-size: 14px; color: {color};'>"
                        f"🩺 <strong>Trạng thái:</strong> {status} &nbsp;<br/>"
                        f"<strong>Độ tin cậy: </strong>{confidence_text}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='font-size: 14px; color: {color};'>🩺 <strong>Trạng thái:</strong> {status}</div>",
                        unsafe_allow_html=True
                    )

    st.divider()

def show_charts(sensor_groups):
    st.markdown("## 📈 Biểu Đồ Biến Thiên")
    for sensor, df in sensor_groups.items():
        with st.container():
            sensor_icon = get_sensor_icon(sensor)
            st.markdown(f"### {sensor_icon} {sensor}")

            # Giới hạn trục Y ±1
            vmin = df['value'].min() - 1
            vmax = df['value'].max() + 1
            unit = get_unit(sensor)

            chart = alt.Chart(df.reset_index()).mark_line(color="#1f77b4").encode(
                x=alt.X('time:T', title='Thời điểm'),
                y=alt.Y('value:Q', title=f'Giá trị ({unit})' if unit else 'Giá trị',
                        scale=alt.Scale(domain=[vmin, vmax]))
            ).properties(height=300, width='container')

            st.altair_chart(chart, use_container_width=True)

            st.divider()

import streamlit as st

# ... (các import và hàm hiện có)

def show_profile(name: str, age: int, address: str, gender: str):
    """
    Hiển thị Thông Tin Hồ Sơ Cá Nhân: Tên, Tuổi, Địa chỉ, Giới tính.
    """
    st.markdown("### Hồ Sơ Cá Nhân")
    # Dùng container để có thể căn chỉnh nếu cần
    with st.container():
        # Tạo hai cột: bên trái là label, bên phải là giá trị
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**Tên:**")
            st.markdown("**Tuổi:**")
            st.markdown("**Địa chỉ:**")
            st.markdown("**Giới tính:**")
        with col2:
            st.markdown(f"{name}")
            st.markdown(f"{age}")
            st.markdown(f"{address}")
            st.markdown(f"{gender}")

    st.divider()

