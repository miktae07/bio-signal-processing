import numpy as np

def analyze_ecg_data(ecg_data):
    """
    Phân tích dữ liệu ECG và trả về các thông số chính.
    """
    return {
        'mean': np.mean(ecg_data),
        'std': np.std(ecg_data),
        'min': np.min(ecg_data),
        'max': np.max(ecg_data)
    }
