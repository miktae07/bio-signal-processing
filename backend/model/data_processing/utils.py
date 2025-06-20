# utils.py
import pandas as pd
from datetime import datetime
from typing import Dict, Any


def map_lang(class_name: str) -> str:
    """Map English ECG class codes to Vietnamese descriptions."""
    lang_map = {
        'N': 'Nhịp bình thường',
        'S': 'Nhịp ngoại tâm thu thất trên',
        'V': 'Nhịp ngoại tâm thu thất',
        'F': 'Nhịp hợp nhất',
        'Q': 'Nhịp không xác định'
    }
    return lang_map.get(class_name, class_name)


def filter_by_time(df: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
    """
    Lọc DataFrame ECG theo khoảng thời gian.

    Args:
        df: DataFrame có cột 'timestamp' (datetime dtype).
        start: thời điểm bắt đầu (inclusive).
        end: thời điểm kết thúc (inclusive).

    Returns:
        DataFrame chỉ chứa các bản ghi giữa start và end.
    """
    # Đảm bảo cột timestamp đúng dtype
    if df['timestamp'].dtype == object:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    mask = (df['timestamp'] >= start) & (df['timestamp'] <= end)
    return df.loc[mask]


def compute_window_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Tính các thống kê cơ bản cho cửa sổ dữ liệu ECG.

    Args:
        series: Pandas Series chứa giá trị ECG số (float).

    Returns:
        Dict gồm mean, std, min, max.
    """
    return {
        'mean': float(series.mean()),
        'std': float(series.std()),
        'min': float(series.min()),
        'max': float(series.max())
    }
