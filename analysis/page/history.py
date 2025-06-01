import streamlit as st
import altair as alt
import pandas as pd
from io import StringIO
from utils.firebase_utils import get_sensor_groups

def show_history_page():
    """
    Trang xem lịch sử dữ liệu cảm biến
    """
    st.header("Lịch Sử Dữ Liệu")

    # Lấy dữ liệu từ Firebase
    sensor_groups = get_sensor_groups()

    if not sensor_groups:
        st.warning("⚠️ Không có dữ liệu lịch sử từ Firebase.")
        return

    # Giao diện chọn  và cảm biến
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("📅 Từ ngày")
    with col2:
        end = st.date_input("📅 Đến ngày")

    selected_sensors = st.multiselect("🔎 Chọn sensor", list(sensor_groups.keys()), default=list(sensor_groups.keys()))

    if st.button("📤 Tải dữ liệu"):
        for sensor in selected_sensors:
            df = sensor_groups[sensor]
            df_range = df.loc[str(start):str(end)].reset_index()

            if df_range.empty:
                st.info(f"Không có dữ liệu cho {sensor} trong khoảng  đã chọn.")
                continue

            st.subheader(f"📊 {sensor}")

            # Hiển thị biểu đồ
            chart = alt.Chart(df_range).mark_line().encode(
                x='time:T',
                y='value:Q'
            ).properties(title=f"Dữ liệu {sensor} từ {start} đến {end}")

            st.altair_chart(chart, use_container_width=True)

            # Hiển thị bảng dữ liệu
            st.dataframe(df_range)

            # Chuyển DataFrame sang CSV để tải
            csv_buffer = StringIO()
            df_range.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()

            st.download_button(
                label=f"📥 Tải dữ liệu {sensor} dưới dạng CSV",
                data=csv_data,
                file_name=f"data_{sensor}_{start}_{end}.csv",
                mime="text/csv"
            )
