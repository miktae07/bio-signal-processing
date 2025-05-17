import streamlit as st
import altair as alt

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
    elif "TEMP" in sensor or "NHIỆT" in sensor:
        return "🌡️"  # Nhiệt độ
    elif "HUM" in sensor or "ĐỘ ẨM" in sensor:
        return "💧"  # Độ ẩm
    else:
        return "🔧"  # Mặc định

import streamlit as st

def show_metrics(sensor_groups):
    st.markdown("## 📊 Dữ liệu Hiện Tại")
    with st.container():
        cols = st.columns(len(sensor_groups))

        for i, (sensor, df) in enumerate(sensor_groups.items()):
            with cols[i]:
                value = df['value'].iloc[-1]
                timestamp = df.index[-1]
                unit = get_unit(sensor)
                icon = get_sensor_icon(sensor)
                display_label = f"{icon} {sensor}"
                display_value = f"{value:.2f} {unit}" if unit else f"{value:.2f}"

                # 🟩 1. Thẻ số liệu có border
                st.metric(label=display_label, value=display_value, delta=None, border=True)

                # 🟩 2. Hiển thị thời gian in đậm
                st.markdown(
                    f"<div style='margin-top: -10px; font-size: 14px; color: #555;'>🕒 <strong>{timestamp.strftime('%d-%m-%Y %H:%M:%S')}</strong></div>",
                    unsafe_allow_html=True
                )

                # 🟩 3. Hiển thị trạng thái sức khỏe
                status = "✅ Khỏe mạnh"  # Placeholder cho xử lý sau
                st.markdown(
                    f"<div style='font-size: 14px; color: green;'>🩺 <strong>Trạng thái:</strong> {status}</div>",
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
