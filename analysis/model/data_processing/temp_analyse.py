from model.data_processing.utils import *
from model.analyse import filter_by_time, compute_window_stats

def analyze_temp_window(df_temp: pd.DataFrame, start: datetime, end: datetime) -> Tuple[Dict[str, float], str]:
    """
    Phân tích một giá trị nhiệt độ đơn lẻ và trả về thống kê cùng trạng thái.

    Tham số:
        temp_value (float): Giá trị nhiệt độ cần phân tích.

    Trả về:
        Tuple:
            - Dict gồm mean, min, max (đều bằng temp_value)
            - Chuỗi mô tả trạng thái nhiệt độ
    """
    window = filter_by_time(df_temp, start, end)['value']   
    stats = compute_window_stats(window)
    temp_value = stats['mean']

    if pd.isna(temp_value):
        return {"mean": None, "min": None, "max": None}, "Không có dữ liệu nhiệt độ"

    if temp_value < 35.0:
        status = "Hạ thân nhiệt (nhiệt độ < 35°C)"
    elif temp_value > 37.5:
        status = "Sốt (nhiệt độ > 37.5°C)"
    else:
        status = "Nhiệt độ bình thường (35–37.5°C)"

    return stats, status
