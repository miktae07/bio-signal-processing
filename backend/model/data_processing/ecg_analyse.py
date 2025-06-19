import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from datetime import datetime
from typing import Union, Dict, Tuple
import streamlit as st
import numpy as np

from .utils import map_lang
from analyse import filter_by_time, compute_window_stats
from tensorflow.keras.models import load_model
from scipy import signal
from pathlib import Path
import numpy as np
from datetime import datetime

# Mapping classes
default_CLASS_MAPPING = {
    0: 'N',  # Non-ecotic beats (normal beat)
    1: 'S',  # Supraventricular ectopic beats
    2: 'V',  # Ventricular ectopic beats
    3: 'F',  # Fusion Beats
    4: 'Q'   # Unknown Beats
}

CLASS_MAPPING = default_CLASS_MAPPING

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"

# ------------------ Preprocess ECG ------------------
def preprocess_ecg_signal(input_signal, sampling_rate=400, target_length=186):
    """
    Tiền xử lý tín hiệu ECG theo chuẩn MIT-BIH (đã điều chỉnh cho tín hiệu ngắn)
    Args:
        input_signal: numpy array tín hiệu ECG thô
        sampling_rate: tần số mẫu (Hz)
        target_length: độ dài mục tiêu sau xử lý
    Returns:
        list chứa 1 beat đã normalize, resampled, padding/truncation
    """
    print(f"[DEBUG] Using sampling_rate = {sampling_rate} Hz")
    print(f"Processing signal with {len(input_signal)} samples at {sampling_rate}Hz")

    # absolute + normalize
    input_signal = np.abs(input_signal)
    if np.ptp(input_signal) > 0:
        normalized_signal = (input_signal - input_signal.min()) / np.ptp(input_signal)
    else:
        normalized_signal = input_signal.copy()

    print(f"[DEBUG] Normalized range: {normalized_signal.min():.2f} to {normalized_signal.max():.2f}")

    # resample to 125Hz
    newsize = int((len(normalized_signal) * 125 / sampling_rate) + 0.5)
    resampled_signal = signal.resample(normalized_signal, newsize)
    print(f"[DEBUG] Resampled signal at 125 Hz, length = {len(resampled_signal)} samples")

    # adjust length
    if len(resampled_signal) > target_length:
        start_idx = (len(resampled_signal) - target_length) // 2
        resampled_signal = resampled_signal[start_idx:start_idx + target_length]
        print(f"[DEBUG] Truncated to {target_length} samples")
    else:
        zerocount = target_length - len(resampled_signal)
        resampled_signal = np.pad(resampled_signal, (0, zerocount), 'constant')
        print(f"[DEBUG] Padded with {zerocount} zeros to reach {target_length} samples")

    return [resampled_signal]

# ---------------- Predict ECG ----------------
def predict_ecg(input_signal, sampling_rate=400, class_mapping=default_CLASS_MAPPING):
    model_path = WEIGHTS_DIR / 'best_ecg_model.h5'
    model = load_model(model_path)

    processed_beats = preprocess_ecg_signal(input_signal, sampling_rate)
    results = []
    for i, beat in enumerate(processed_beats):
        x = beat.reshape(1, -1, 1)
        pred = model.predict(x, verbose=0)[0]
        idx = np.argmax(pred)
        results.append({
            'beat_index': i+1,
            'predicted_class': idx,
            'class_name': class_mapping[idx],
            'confidence': float(np.max(pred)),
            'probabilities': pred.tolist()
        })
    return results


def predict_single_beat(input_signal, sampling_rate=400, class_mapping=default_CLASS_MAPPING):
    res = predict_ecg(input_signal, sampling_rate, class_mapping)
    if res:
        return res[0]['predicted_class'], res[0]['confidence'], res[0]['class_name']
    return None, 0.0, 'No Data'

# ---------------- Cardiac Metrics ----------------
def compute_cardiac_metrics(ecg_signal: np.ndarray, fs: int = 125):
    """
    Tính HR, RR intervals, RR mean, RR std từ tín hiệu ECG đã xử lý.
    ecg_signal: 1D array ở fs Hz
    fs: sampling rate
    """
    distance = int(0.2 * fs)
    peaks, _ = signal.find_peaks(ecg_signal, height=0.5, distance=distance)
    if len(peaks) < 2:
        return {'hr_mean': 0.0, 'rr_intervals': [], 'rr_mean': 0.0, 'rr_std': 0.0}

    rr_samples = np.diff(peaks)
    rr = rr_samples / fs
    rr_mean = np.mean(rr)
    rr_std = np.std(rr)
    hr = 60.0 / rr_mean if rr_mean > 0 else 0.0
    return {'hr_mean': hr, 'rr_intervals': rr.tolist(), 'rr_mean': rr_mean, 'rr_std': rr_std}


def count_beats(ecg_signal: np.ndarray, fs: int = 125):
    distance = int(0.2 * fs)
    peaks, _ = signal.find_peaks(ecg_signal, height=0.5, distance=distance)
    return len(peaks), peaks

# ---------------- Analyze Window ----------------
def analyze_ecg_window(
    df_ECG, start=datetime, end=None
):
    if pd.api.types.is_integer_dtype(df_ECG['timestamp']):
        df_ECG['timestamp'] = pd.to_datetime(df_ECG['timestamp'], unit='s')  # Adjust unit if needed (e.g., 'ms')
    
    # Handle None values for start and end
    if start is None:
        start = df_ECG['timestamp'].min()
    if end is None:
        end = df_ECG['timestamp'].max()
    # Nếu không truyền start/end hoặc không phải datetime, dùng toàn bộ
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        series = df_ECG['value']
        print("[DEBUG] No valid time window provided, using full series.")
    else:
        series = filter_by_time(df_ECG, start, end)['value']
        print(f"[DEBUG] Filtering between {start} and {end}, got {len(series)} samples.")

    if series.empty:
        return {
            'stats': {'mean':0,'std':0,'min':0,'max':0},
            'class_name':'No Data',
            'confidence':0.0,
            'cardiac_metrics': {'hr_mean':0,'rr_intervals':[],'rr_mean':0,'rr_std':0},
            'sampling_rate':0,
            'num_beats':0
        }

    stats = compute_window_stats(series)
    arr = series.to_numpy(dtype=float)

    # Sampling rate sau preprocess luôn 125Hz
    fs = 125
    print(f"[DEBUG] Sampling rate of windowed ECG: {fs} Hz")

    # Đếm beats
    num_beats, peak_idxs = count_beats(arr, fs)
    print(f"[DEBUG] Detected R-peaks at indices: {peak_idxs}")
    print(f"[DEBUG] Number of beats in window: {num_beats}")

    # Classification (dùng toàn chuỗi)
    _, confidence, class_name = predict_single_beat(arr, sampling_rate=400)
    class_name = map_lang(class_name)

    # Metrics HR/RR
    cardiac_metrics = compute_cardiac_metrics(arr, fs)

    return {
        'stats': stats,
        'class_name': class_name,
        'confidence': confidence,
        'cardiac_metrics': cardiac_metrics,
        'sampling_rate': fs,
        'num_beats': num_beats
    }