from model.data_processing.utils import *
from model.analyse import filter_by_time, compute_window_stats

def analyze_spo2_window(
    df_spo2: pd.DataFrame, start: datetime, end: datetime
) -> Tuple[Dict[str, float], str]:
    """
    Lọc dữ liệu SpO2 và trả về thống kê cùng trạng thái.

    Returns:
      stats: dict mean/max/min
      status: str mô tả tình trạng SpO2
    """
    window = filter_by_time(df_spo2, start, end)['value']
    if len(window) == 0:
        return {}, "Không có dữ liệu SpO2"
    print ("DEBUG- window SpO2", window)
    stats = compute_window_stats(window)
    mean = stats['mean']
    #https://my.clevelandclinic.org/health/diagnostics/22447-blood-oxygen-level
    #https://www.vinmec.com/vie/bai-viet/chi-so-spo2-o-nguoi-binh-thuong-la-bao-nhieu-vi
    print("DEBUG- mean SpO2", mean)

    if pd.isna(mean):
        status = "Không có dữ liệu SpO2"
    elif mean < 90:
        status = "Suy hô hấp nặng (SpO2 < 90%)"
    elif mean < 95:
        status = "Suy hô hấp nhẹ (90% ≤ SpO2 < 95%)"
    else:
        status = "SpO2 bình thường (≥ 95%)"

    return stats, status