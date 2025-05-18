import pandas as pd
from datetime import datetime
from typing import Union, Dict, Tuple


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
    stats = compute_window_stats(window)
    mean = stats['mean']
    #https://my.clevelandclinic.org/health/diagnostics/22447-blood-oxygen-level
    #https://www.vinmec.com/vie/bai-viet/chi-so-spo2-o-nguoi-binh-thuong-la-bao-nhieu-vi

    if pd.isna(mean):
        status = "Không có dữ liệu SpO2"
    elif mean < 90:
        status = "Suy hô hấp nặng (SpO2 < 90%)"
    elif mean < 95:
        status = "Suy hô hấp nhẹ (90% ≤ SpO2 < 95%)"
    else:
        status = "SpO2 bình thường (≥ 95%)"

    return stats, status


def evaluate_health(
    bpm_stats: Dict[str, float], bpm_status: str,
    spo2_stats: Dict[str, float], spo2_status: str
) -> str:
    """
    Đánh giá chung kết hợp BPM và SpO2.

    Returns:
      overall: kết luận chung
    """
    if bpm_status == "Nhịp tim bình thường" and spo2_status.startswith("SpO₂ bình thường"):
        return "Sức khỏe bình thường"
    issues = []
    if bpm_status != "Nhịp tim bình thường":
        issues.append(bpm_status)
    if not spo2_status.startswith("SpO₂ bình thường"):
        issues.append(spo2_status)
    return "; ".join(issues) if issues else "Không xác định"
