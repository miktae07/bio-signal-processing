from model.data_processing.utils import *
from model.analyse import filter_by_time, compute_window_stats

def analyze_bpm_window(
    df_bpm: pd.DataFrame, start: datetime, end: datetime
) -> Tuple[Dict[str, float], str]:
    """
    Lọc dữ liệu BPM và trả về thống kê cùng trạng thái.

    Returns:
      stats: dict mean/max/min
      status: str mô tả tình trạng BPM
    """
    window = filter_by_time(df_bpm, start, end)['value']
    stats = compute_window_stats(window)
    mean = stats['mean']

    # https://www.vinmec.com/vie/bai-viet/chi-so-bpm-trong-dien-tim-hieu-nhu-nao-vi
    # https://www.health.harvard.edu/heart-health/what-your-heart-rate-is-telling-you
    if pd.isna(mean):
        status = "Không có dữ liệu BPM"
    elif mean < 60:
        status = "Nhịp tim chậm (Bradycardia)"
    elif mean <= 100:
        status = "Nhịp tim bình thường"
    else:
        status = "Nhịp tim nhanh (Tachycardia)"

    return stats, status