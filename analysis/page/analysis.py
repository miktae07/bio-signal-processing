import streamlit as st
import pandas as pd
from datetime import datetime, time
from utils.utils import map_vietnamese_to_english
from utils.firebase_utils import get_sensor_groups
from model.data_processing.bpm_analyse import analyze_bpm_window
from model.data_processing.spo2_analyse import analyze_spo2_window
from model.data_processing.ecg_analyse import analyze_ecg_window
from model.analyse import process_signal, evaluate_health
from utils.components import show_charts

def show_analysis_page():
    """
    Trang phân tích dữ liệu cảm biến BPM, SpO2, ECG…
    - Chỉ hiển thị chart cho các sensor được chọn và trong khoảng  đã chọn.
    """
    st.header("Phân Tích Dữ Liệu Y Tế")

    # 1. Lấy dữ liệu từ Firebase
    sensor_groups = get_sensor_groups()
    if not sensor_groups:
        st.warning("⚠️ Không tìm thấy dữ liệu để phân tích.")
        return

    # 2. Tạo name_to_key tự động map mỗi key trong sensor_groups → chính nó
    name_to_key = { key: key for key in sensor_groups.keys() }

    # 3. Hiển thị multiselect cho tất cả các key hiện có
    available_signals = list(name_to_key.keys())
    selected = st.multiselect(
        "Chọn tín hiệu phân tích",
        options=available_signals,
        default=[]  # hoặc default=available_signals nếu muốn mặc định chọn hết
    )

    # 4. Chọn khoảng ngày giờ
    times = [time(hour=h, minute=m) for h in range(24) for m in range(0, 60, 5)]

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Ngày bắt đầu", value=pd.to_datetime("2025-01-01"))
        # Dùng selectbox để chọn giờ (với các giá trị cách nhau 5 phút)
        start_time = st.selectbox("Giờ bắt đầu", options=times, index=0)

    with col2:
        end_date = st.date_input("Ngày kết thúc", value=pd.to_datetime("2025-12-31"))
        end_time = st.selectbox("Giờ kết thúc", options=times, index=len(times)-1)

    start_dt = datetime.combine(start_date, start_time)
    end_dt   = datetime.combine(end_date, end_time)

    # 5. Khi bấm nút "Chạy phân tích"
    if st.button("🔍 Chạy phân tích"):
        if start_dt > end_dt:
            st.error("⚠️ Thời điểm bắt đầu phải nhỏ hơn hoặc bằng thời điểm kết thúc.")
            return

        export_data  = []  # list để lưu từng dòng (Data Type, Timestamp, Value, Analysis Result)
        summary_rows = []  # list để lưu summary (Data Type, Min, Max, Mean, Analysis Result)

        # 6. Lọc và vẽ chart cho từng sensor được chọn ngay khi bấm nút
        if selected:
            # Tạo dict chứa DataFrame đã lọc theo time window cho mỗi sensor trong selected
            filtered_groups = {}
            for sig in selected:
                if sig in sensor_groups:
                    df_orig = sensor_groups[sig]
                    # Giả sử df_orig có index là datetime; nếu không, bạn cần convert:
                    #     df_orig = df_orig.set_index('timestamp')
                    df_filt = df_orig.loc[(df_orig.index >= start_dt) & (df_orig.index <= end_dt)]
                    filtered_groups[sig] = df_filt

            # Nếu có ít nhất 1 sensor có data trong khoảng , vẽ chart
            # Nếu filtered_groups rỗng (hoặc các df_filt đều empty), show thông báo
            if any(not df.empty for df in filtered_groups.values()):
                show_charts(filtered_groups)
            else:
                st.write("Không có dữ liệu để vẽ biểu đồ trong khoảng đã chọn.")
        else:
            st.warning("Chưa chọn tín hiệu nào để phân tích.")

        # 7. Xử lý tuần tự cho từng signal được chọn (chạy các hàm analyze_... để thu export_data & summary_rows)
        for sig in selected:
            key = name_to_key[sig]

            st.subheader(f"Phân tích {sig}")
            if sig == 'BPM':
                process_signal(
                    key_in_groups=key,
                    display_name='BPM',
                    analyze_fn=analyze_bpm_window,
                    unit_str=' bpm',
                    sensor_groups=sensor_groups,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    export_data=export_data,
                    summary_rows=summary_rows
                )
            elif sig == 'SpO2':
                process_signal(
                    key_in_groups=key,
                    display_name='SpO₂',
                    analyze_fn=analyze_spo2_window,
                    unit_str='%',
                    sensor_groups=sensor_groups,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    export_data=export_data,
                    summary_rows=summary_rows
                )
            elif sig == 'ECG':
                process_signal(
                    key_in_groups=key,
                    display_name='ECG',
                    analyze_fn=analyze_ecg_window,
                    unit_str='μV',
                    sensor_groups=sensor_groups,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    export_data=export_data,
                    summary_rows=summary_rows
                )
            else:
                st.warning(f"⚠️ Chưa có hàm phân tích cho tín hiệu: {sig}. Đã bỏ qua.")

        # 8. Nếu có data để xuất CSV và hiển thị bảng
        if export_data:
            df_export = pd.DataFrame(
                export_data,
                columns=["Data Type", "Timestamp", "Value", "Analysis Result"]
            )
            st.markdown("### 📋 Bảng Kết Quả Phân Tích")
            st.download_button(
                label="📥 Tải về CSV",
                data=df_export.to_csv(index=False, encoding='utf-8-sig'),
                file_name="ket_qua_phan_tich.csv",
                mime="text/csv"
            )
            st.dataframe(df_export)

        # 9. Hiển thị summary (chỉ những tín hiệu đã được phân tích)
        if summary_rows:
            df_summary = pd.DataFrame(
                summary_rows,
                columns=["Data Type", "Min", "Max", "Mean", "Analysis Result"]
            )
            st.subheader("📊 Tổng hợp theo loại dữ liệu")
            st.dataframe(df_summary)
