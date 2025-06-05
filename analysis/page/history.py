import streamlit as st
import altair as alt
import pandas as pd
from io import StringIO
import datetime
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

    # Mặc định từ 1.1.2025 đến ngày hiện tại
    default_start_dt = datetime.datetime(2025, 1, 1, 0, 0)
    default_end_dt = datetime.datetime.now()
    default_start_date = default_start_dt.date()
    default_start_time = default_start_dt.time()
    default_end_date = default_end_dt.date()
    default_end_time = default_end_dt.time()

    # Giao diện chọn ngày và giờ
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Từ ngày", value=default_start_date)
        start_time = st.time_input("⏰ Từ giờ", value=default_start_time)
    with col2:
        end_date = st.date_input("📅 Đến ngày", value=default_end_date)
        end_time = st.time_input("⏰ Đến giờ", value=default_end_time)

    # Kết hợp ngày và giờ
    start = datetime.datetime.combine(start_date, start_time)
    end = datetime.datetime.combine(end_date, end_time)

    selected_sensors = st.multiselect("🔎 Chọn sensor", list(sensor_groups.keys()), default=list(sensor_groups.keys()))

    if st.button("📤 Tải dữ liệu"):
        for sensor in selected_sensors:
            df = sensor_groups[sensor]

            # Chuyển index thành datetime để lọc
            df.index = pd.to_datetime(df.index)
            # Lọc theo khoảng thời gian
            df_range = df.loc[start: end].reset_index()

            if df_range.empty:
                st.info(f"Không có dữ liệu cho {sensor} trong khoảng đã chọn.")
                continue

            st.subheader(f"📊 {sensor}")

            # Đổi tên cột index thành time nếu cần
            if 'index' in df_range.columns:
                df_range.rename(columns={'index': 'time'}, inplace=True)

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
                file_name=f"data_{sensor}_{start.strftime('%Y%m%d_%H%M')}_{end.strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
