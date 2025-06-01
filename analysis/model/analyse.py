import pandas as pd
from datetime import datetime
from typing import Union, Dict, Tuple
import streamlit as st
from utils.utils import map_vietnamese_to_english

def process_signal(
    key_in_groups: str,
    display_name: str,
    analyze_fn: callable,
    unit_str: str,
    sensor_groups: dict,
    start_dt: datetime,
    end_dt: datetime,
    export_data: list,
    summary_rows: list
):
    """
    Hàm chung để lấy DataFrame của một tín hiệu, kiểm tra cột 'value', lọc khoảng ,
    gọi hàm analyze_fn để tính stats và trạng thái (status), rồi xuất ra Streamlit và
    thêm vào export_data, summary_rows.
    
    - key_in_groups:     tên key thực tế trong sensor_groups (ví dụ 'BPM', 'SpO2', 'ECG', ...)
    - display_name:      tên hiển thị (để in ra trên giao diện, ví dụ 'BPM', 'SpO₂', 'ECG')
    - analyze_fn:        hàm phân tích tương ứng, nhận (df, start_dt, end_dt) → trả về (stats_dict, status_vn)
    - unit_str:          chuỗi đơn vị khi in (ví dụ ' bpm' cho BPM, '%' cho SpO₂, ...)
    - sensor_groups:     dict lấy từ Firebase (key → DataFrame)
    - start_dt, end_dt:  datetime để lọc
    - export_data:       list chung để append từng dòng CSV (được pass tham chiếu từ ngoài)
    - summary_rows:      list chung để append summary (min, max, mean, status) (được pass tham chiếu từ ngoài)
    
    Trả về: tuple (stats_dict, status_vn) nếu thành công, hoặc None nếu có lỗi (Streamlit đã show error rồi).
    """
    # 1. Lấy DataFrame từ sensor_groups
    df = sensor_groups[key_in_groups].copy()
    
    # 2. Kiểm tra xem có cột 'value' hay không
    if 'value' not in df.columns:
        st.error(f"❌ Dữ liệu {display_name} không chứa cột 'value'. Vui lòng kiểm tra dữ liệu.")
        return None
    
    # 3. Lọc khoảng 
    df = df[(df.index >= start_dt) & (df.index <= end_dt)]
    
    # 4. Gọi hàm phân tích chuyên biệt (vd: analyze_bpm_window, analyze_spo2_window, ...)
    if(display_name == 'ECG'):
        stats, status_vn, confidence = analyze_fn(df, start_dt, end_dt)
    else:
        stats, status_vn = analyze_fn(df, start_dt, end_dt)
    status_en = map_vietnamese_to_english(status_vn)

    # 5. In kết quả lên Streamlit
    st.subheader(f"Kết quả phân tích {display_name}")
    st.write(f"- Trung bình: {stats['mean']:.1f}{unit_str}")
    st.write(f"- Min: {stats['min']:.1f}{unit_str}")
    st.write(f"- Max: {stats['max']:.1f}{unit_str}")
    st.write(f"- Trạng thái: **{status_vn}**")
    if(display_name == 'ECG'):
        st.write(f"- Độ tin cậy: {confidence: .2f}")

    # 6. Append từng dòng dữ liệu vào export_data (để xuất CSV)
    for idx, row in df.iterrows():
        export_data.append([
            display_name, 
            idx, 
            row['value'], 
            status_en
        ])
    
    # 7. Append summary (min, max, mean, status_en) vào summary_rows
    summary_rows.append([
        display_name,
        stats['min'],
        stats['max'],
        stats['mean'],
        status_en
    ])
    
    # 8. Trả về để nếu cần tính evaluate tổng quát có thể dùng lại
    return stats, status_vn

def filter_by_time(df: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
    """
    Lọc DataFrame theo index datetime trong khoảng [start, end].
    """
    return df[(df.index >= start) & (df.index <= end)]


def compute_window_stats(data: Union[pd.Series, list]) -> Dict[str, float]:
    """
    Tính mean, max, min cho chuỗi dữ liệu.

    Args:
      data: pd.Series hoặc list các giá trị số.

    Returns:
      dict với keys 'mean', 'max', 'min'.
    """
    series = pd.Series(data) if not isinstance(data, pd.Series) else data
    return {
        'mean': series.mean(),
        'max': series.max(),
        'min': series.min()
    }

def evaluate_health(
    status_bpm: str,
    status_spo2: str,
    status_ecg: str
) -> Tuple[str, str]:
    """
    Đánh giá tình trạng sức khỏe tổng quát.
    """
    overall_status = "Khỏe mạnh"  # Default status

    if status_bpm != "Bình thường" or status_spo2 != "Bình thường" or status_ecg != "Bình thường":
        overall_status = "Cần chú ý"
    
    return overall_status, status_ecg