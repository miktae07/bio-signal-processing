import os

# Khoảng refresh trang
AUTO_REFRESH_INTERVAL_MS = 10_000  # 10 giây

# Đường dẫn hoặc cấu hình khác tùy dự án
DATA_PATH = "./data"
LOG_PATH = "./logs"

# utils.py

def map_lang(text):
    mapping = {
        "Nhịp tim chậm (Bradycardia)": "Bradycardia (Slow heart rate)",
        "Nhịp tim bình thường": "Normal heart rate",
        "Nhịp tim nhanh (Tachycardia)": "Tachycardia (Fast heart rate)",
        "Không có dữ liệu BPM": "No BPM data",
        "Suy hô hấp nặng (SpO2 < 90%)": "Severe respiratory failure (SpO2 < 90%)",
        "Suy hô hấp nhẹ (90% ≤ SpO2 < 95%)": "Mild respiratory failure (90% ≤ SpO2 < 95%)",
        "SpO2 bình thường (≥ 95%)": "Normal SpO2 (≥ 95%)",
        "Không có dữ liệu SpO2": "No SpO2 data",
        "N": "Nhịp tim bình thường(N)",
        "S": "Nhịp trên thất ngoại tâm thu(S)",
        "V": "Nhịp thất ngoại tâm thu(V)",
        "F": "Nhịp hợp tử(F)",
        "Q": "Nhịp không xác định(Q)",
        "BPM": "Nhịp tim(BPM)",
        "ECG": "Điện tim(ECG)",
        "SpO2" : "Nồng độ Oxy trong máu(SpO2)",
        "Temp" : "Nhiệt độ cơ thể"
    }
    return mapping.get(text, text)

def get_model_path(filename="best_unet_resnet18_model.keras"):
    cwd = os.getcwd()
    print(f"[DEBUG] Current working directory: {cwd}")
    # Nếu đang ở thư mục analysis
    if os.path.isdir(os.path.join(cwd, "model", "weights")):
        path = os.path.join(cwd, "model", "weights", filename)
    # Ngược lại giả định đang ở root bio-signal-processing
    else:
        path = os.path.join(cwd, "analysis", "model", "weights", filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy model tại: {path}")
    return path
