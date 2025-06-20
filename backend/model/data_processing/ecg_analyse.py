import sys
import os
from datetime import datetime
import pandas as pd
from typing import Union, Dict, Tuple
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .utils import map_lang, filter_by_time, compute_window_stats
from tensorflow.keras.models import load_model
from scipy import signal
from pathlib import Path

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
IMAGES_DIR = BASE_DIR / "processing_images"
IMAGES_DIR.mkdir(exist_ok=True)

# ---------------- Helper to build unique filepath ----------------
def _make_unique_filepath(filename: str, save_dir: Path) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    target_dir = save_dir / today
    target_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return target_dir / f"{filename}_{ts}.png"

# ---------------- Image Saving Functions ----------------
def save_signal_plot(signal_data, title, filename, sampling_rate=None, peaks=None, save_dir=None):
    """
    Lưu biểu đồ tín hiệu ECG với tên file có timestamp và trong thư mục theo ngày.
    """
    dir_ = save_dir or IMAGES_DIR
    filepath = _make_unique_filepath(filename, dir_)

    plt.figure(figsize=(12, 6))
    if sampling_rate:
        time_axis = np.arange(len(signal_data)) / sampling_rate
        plt.plot(time_axis, signal_data, 'b-', linewidth=1)
        if peaks is not None:
            plt.plot(time_axis[peaks], signal_data[peaks], 'ro', markersize=8,
                     label=f'R-peaks ({len(peaks)})')
        plt.xlabel('Thời gian (s)')
    else:
        plt.plot(signal_data, 'b-', linewidth=1)
        if peaks is not None:
            plt.plot(peaks, signal_data[peaks], 'ro', markersize=8,
                     label=f'R-peaks ({len(peaks)})')
        plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    if peaks is not None:
        plt.legend()
    stats_text = (
        f"Min: {np.min(signal_data):.3f}\n"
        f"Max: {np.max(signal_data):.3f}\n"
        f"Mean: {np.mean(signal_data):.3f}\n"
        f"Std: {np.std(signal_data):.3f}"
    )
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Saved plot: {filepath}")


def save_comparison_plot(original, processed, title, filename, sampling_rates=None, save_dir=None):
    """
    Lưu biểu đồ so sánh 2 tín hiệu (trước và sau xử lý) có timestamp.
    """
    dir_ = save_dir or IMAGES_DIR
    filepath = _make_unique_filepath(filename, dir_)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    # Original
    if sampling_rates and len(sampling_rates) > 0:
        t1 = np.arange(len(original)) / sampling_rates[0]
        ax1.plot(t1, original, 'r-', linewidth=1, label='Original')
        ax1.set_xlabel('Thời gian (s)')
    else:
        ax1.plot(original, 'r-', linewidth=1, label='Original')
        ax1.set_xlabel('Samples')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Tín hiệu gốc')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    # Processed
    if sampling_rates and len(sampling_rates) > 1:
        t2 = np.arange(len(processed)) / sampling_rates[1]
        ax2.plot(t2, processed, 'b-', linewidth=1, label='Processed')
        ax2.set_xlabel('Thời gian (s)')
    else:
        ax2.plot(processed, 'b-', linewidth=1, label='Processed')
        ax2.set_xlabel('Samples')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('Tín hiệu đã xử lý')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Saved comparison plot: {filepath}")


def save_processing_steps_plot(steps_data, title, filename, save_dir=None):
    """
    Lưu biểu đồ hiển thị nhiều bước xử lý với timestamp.
    """
    dir_ = save_dir or IMAGES_DIR
    filepath = _make_unique_filepath(filename, dir_)
    n = len(steps_data)
    fig, axes = plt.subplots(n, 1, figsize=(12, 3*n))
    if n == 1:
        axes = [axes]
    for i, step in enumerate(steps_data):
        data = step['data']; fs = step.get('sampling_rate')
        peaks = step.get('peaks')
        if fs:
            t = np.arange(len(data)) / fs
            axes[i].plot(t, data, 'b-', linewidth=1)
            if peaks is not None:
                axes[i].plot(t[peaks], data[peaks], 'ro', markersize=6)
            axes[i].set_xlabel('Thời gian (s)')
        else:
            axes[i].plot(data, 'b-', linewidth=1)
            if peaks is not None:
                axes[i].plot(peaks, data[peaks], 'ro', markersize=6)
            axes[i].set_xlabel('Samples')
        axes[i].set_ylabel('Amplitude')
        axes[i].set_title(step['title'])
        axes[i].grid(True, alpha=0.3)
        stats = f"Len: {len(data)}, Min: {np.min(data):.2f}, Max: {np.max(data):.2f}"
        axes[i].text(0.02, 0.95, stats, transform=axes[i].transAxes,
                     verticalalignment='top', fontsize=9,
                     bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Saved processing steps plot: {filepath}")


def save_frequency_analysis_plot(signal_data, sampling_rate, title, filename, save_dir=None):
    """
    Lưu biểu đồ phân tích tần số (FFT) với timestamp.
    """
    dir_ = save_dir or IMAGES_DIR
    filepath = _make_unique_filepath(filename, dir_)
    fft_vals = np.fft.fft(signal_data)
    fft_freq = np.fft.fftfreq(len(signal_data), 1/sampling_rate)
    idx = fft_freq > 0
    freqs = fft_freq[idx]; mags = np.abs(fft_vals[idx])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    # time\    
    t = np.arange(len(signal_data)) / sampling_rate
    ax1.plot(t, signal_data, 'b-', linewidth=1)
    ax1.set_xlabel('Thời gian (s)'); ax1.set_ylabel('Amplitude')
    ax1.set_title('Miền thời gian'); ax1.grid(True, alpha=0.3)
    # freq
    ax2.plot(freqs, mags, 'r-', linewidth=1)
    ax2.set_xlabel('Tần số (Hz)'); ax2.set_ylabel('Magnitude')
    ax2.set_title('Miền tần số (FFT)'); ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, min(50, np.max(freqs)))
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Saved frequency analysis plot: {filepath}")


def save_prediction_results_plot(signal_data, prediction_results, title, filename, sampling_rate=125, save_dir=None):
    """
    Lưu biểu đồ kết quả dự đoán với probability bars, có timestamp.
    """
    dir_ = save_dir or IMAGES_DIR
    filepath = _make_unique_filepath(filename, dir_)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    t = np.arange(len(signal_data)) / sampling_rate
    ax1.plot(t, signal_data, 'b-', linewidth=1)
    ax1.set_xlabel('Thời gian (s)'); ax1.set_ylabel('Amplitude')
    ax1.set_title(
        f"Tín hiệu ECG - Dự đoán: {prediction_results['class_name']} "
        f"(Confidence: {prediction_results['confidence']:.3f})"
    )
    ax1.grid(True, alpha=0.3)
    class_names = list(default_CLASS_MAPPING.values())
    probs = prediction_results['probabilities']
    colors = [
        'green' if i == prediction_results['predicted_class'] else 'lightblue'
        for i in range(len(probs))
    ]
    bars = ax2.bar(class_names, probs, color=colors)
    ax2.set_xlabel('Loại nhịp tim'); ax2.set_ylabel('Xác suất')
    ax2.set_title('Phân bố xác suất các loại nhịp tim'); ax2.grid(True, alpha=0.3, axis='y')
    for bar, p in zip(bars, probs):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                 f"{p:.3f}", ha='center', va='bottom')
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[DEBUG] Saved prediction results plot: {filepath}")

# ------------------ Enhanced Preprocess ECG ------------------
def preprocess_ecg_signal_with_images(input_signal, sampling_rate=400, target_length=186, save_images=True, prefix="ecg"):
    """
    Tiền xử lý tín hiệu ECG với tùy chọn lưu ảnh sau mỗi bước
    """
    print(f"[DEBUG] Using sampling_rate = {sampling_rate} Hz")
    print(f"Processing signal with {len(input_signal)} samples at {sampling_rate}Hz")
    
    steps_data = []
    
    # Step 1: Original signal
    if save_images:
        save_signal_plot(input_signal, "Tín hiệu ECG gốc", f"{prefix}_01_original", sampling_rate)
        steps_data.append({
            'data': input_signal,
            'title': 'Bước 1: Tín hiệu gốc',
            'sampling_rate': sampling_rate
        })
    
    # Step 2: Absolute value
    abs_signal = np.abs(input_signal)
    if save_images:
        save_signal_plot(abs_signal, "Tín hiệu sau khi lấy giá trị tuyệt đối", f"{prefix}_02_absolute", sampling_rate)
        steps_data.append({
            'data': abs_signal,
            'title': 'Bước 2: Giá trị tuyệt đối',
            'sampling_rate': sampling_rate
        })
    
    # Step 3: Normalization
    if np.ptp(abs_signal) > 0:
        normalized_signal = (abs_signal - abs_signal.min()) / np.ptp(abs_signal)
    else:
        normalized_signal = abs_signal.copy()
    
    print(f"[DEBUG] Normalized range: {normalized_signal.min():.2f} to {normalized_signal.max():.2f}")
    
    if save_images:
        save_signal_plot(normalized_signal, "Tín hiệu sau chuẩn hóa", f"{prefix}_03_normalized", sampling_rate)
        steps_data.append({
            'data': normalized_signal,
            'title': 'Bước 3: Chuẩn hóa (0-1)',
            'sampling_rate': sampling_rate
        })
    
    # Step 4: Resampling to 125Hz
    newsize = int((len(normalized_signal) * 125 / sampling_rate) + 0.5)
    resampled_signal = signal.resample(normalized_signal, newsize)
    print(f"[DEBUG] Resampled signal at 125 Hz, length = {len(resampled_signal)} samples")
    
    if save_images:
        save_signal_plot(resampled_signal, "Tín hiệu sau resampling (125Hz)", f"{prefix}_04_resampled", 125)
        save_comparison_plot(normalized_signal, resampled_signal, 
                           "So sánh trước và sau resampling", f"{prefix}_04_resampling_comparison",
                           [sampling_rate, 125])
        steps_data.append({
            'data': resampled_signal,
            'title': 'Bước 4: Resampling (125Hz)',
            'sampling_rate': 125
        })
    
    # Step 5: Length adjustment (padding/truncation)
    if len(resampled_signal) > target_length:
        start_idx = (len(resampled_signal) - target_length) // 2
        final_signal = resampled_signal[start_idx:start_idx + target_length]
        operation = f"Truncated to {target_length} samples"
        print(f"[DEBUG] {operation}")
    else:
        zerocount = target_length - len(resampled_signal)
        final_signal = np.pad(resampled_signal, (0, zerocount), 'constant')
        operation = f"Padded with {zerocount} zeros to reach {target_length} samples"
        print(f"[DEBUG] {operation}")
    
    if save_images:
        save_signal_plot(final_signal, f"Tín hiệu cuối cùng ({operation})", f"{prefix}_05_final", 125)
        steps_data.append({
            'data': final_signal,
            'title': f'Bước 5: Điều chỉnh độ dài ({target_length} samples)',
            'sampling_rate': 125
        })
        
        # Save all steps in one plot
        save_processing_steps_plot(steps_data, "Các bước xử lý tín hiệu ECG", f"{prefix}_all_steps")
        
        # Save frequency analysis
        save_frequency_analysis_plot(final_signal, 125, "Phân tích tần số tín hiệu cuối", f"{prefix}_frequency_analysis")
    
    return [final_signal]

# ---------------- Enhanced Predict ECG ----------------
def predict_ecg_with_images(input_signal, sampling_rate=400, class_mapping=default_CLASS_MAPPING, save_images=True, prefix="prediction"):
    model_path = WEIGHTS_DIR / 'best_ecg_model.h5'
    model = load_model(model_path)

    processed_beats = preprocess_ecg_signal_with_images(input_signal, sampling_rate, save_images=save_images, prefix=prefix)
    results = []
    
    for i, beat in enumerate(processed_beats):
        x = beat.reshape(1, -1, 1)
        pred = model.predict(x, verbose=0)[0]
        idx = np.argmax(pred)
        
        result = {
            'beat_index': i+1,
            'predicted_class': idx,
            'class_name': class_mapping[idx],
            'confidence': float(np.max(pred)),
            'probabilities': pred.tolist()
        }
        results.append(result)
        
        if save_images:
            save_prediction_results_plot(beat, result, 
                                       f"Kết quả dự đoán - Beat {i+1}", 
                                       f"{prefix}_beat_{i+1}_prediction")
    
    return results

def predict_single_beat_with_images(input_signal, sampling_rate=400, class_mapping=default_CLASS_MAPPING, save_images=True, prefix="single_beat"):
    res = predict_ecg_with_images(input_signal, sampling_rate, class_mapping, save_images, prefix)
    if res:
        return res[0]['predicted_class'], res[0]['confidence'], res[0]['class_name']
    return None, 0.0, 'No Data'

# ---------------- Enhanced Cardiac Metrics ----------------
def compute_cardiac_metrics_with_images(ecg_signal: np.ndarray, fs: int = 125, save_images=True, prefix="metrics"):
    """
    Tính HR, RR intervals với visualization
    """
    distance = int(0.2 * fs)
    peaks, properties = signal.find_peaks(ecg_signal, height=0.5, distance=distance)
    
    if save_images:
        save_signal_plot(ecg_signal, f"Phát hiện R-peaks ({len(peaks)} peaks)", 
                        f"{prefix}_r_peaks", fs, peaks)
    
    if len(peaks) < 2:
        return {'hr_mean': 0.0, 'rr_intervals': [], 'rr_mean': 0.0, 'rr_std': 0.0}

    rr_samples = np.diff(peaks)
    rr = rr_samples / fs
    rr_mean = np.mean(rr)
    rr_std = np.std(rr)
    hr = 60.0 / rr_mean if rr_mean > 0 else 0.0
    
    if save_images:
        # Plot RR intervals
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(rr, 'bo-', linewidth=1, markersize=4)
        plt.ylabel('RR Interval (s)')
        plt.title(f'RR Intervals (Mean: {rr_mean:.3f}s, Std: {rr_std:.3f}s)')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 1, 2)
        plt.hist(rr, bins=min(10, len(rr)), alpha=0.7, edgecolor='black')
        plt.xlabel('RR Interval (s)')
        plt.ylabel('Frequency')
        plt.title(f'RR Interval Distribution (HR: {hr:.1f} bpm)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = IMAGES_DIR / f"{prefix}_rr_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[DEBUG] Saved RR analysis plot: {filepath}")
    
    return {'hr_mean': hr, 'rr_intervals': rr.tolist(), 'rr_mean': rr_mean, 'rr_std': rr_std}

def count_beats_with_images(ecg_signal: np.ndarray, fs: int = 125, save_images=True, prefix="beats"):
    distance = int(0.2 * fs)
    peaks, _ = signal.find_peaks(ecg_signal, height=0.5, distance=distance)
    
    if save_images:
        save_signal_plot(ecg_signal, f"Đếm beats: {len(peaks)} beats được phát hiện", 
                        f"{prefix}_count", fs, peaks)
    
    return len(peaks), peaks

# ---------------- Enhanced Analyze Window ----------------
def analyze_ecg_window_with_images(
    df_ECG, start=datetime, end=None, save_images=True, prefix="window_analysis"
):
    if pd.api.types.is_integer_dtype(df_ECG['timestamp']):
        df_ECG['timestamp'] = pd.to_datetime(df_ECG['timestamp'], unit='s')
    
    if start is None:
        start = df_ECG['timestamp'].min()
    if end is None:
        end = df_ECG['timestamp'].max()
    
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
    fs = 125

    if save_images:
        save_signal_plot(arr, f"Cửa sổ phân tích ECG ({len(arr)} samples)", 
                        f"{prefix}_windowed_signal", fs)
    
    # Đếm beats với hình ảnh
    num_beats, peak_idxs = count_beats_with_images(arr, fs, save_images, f"{prefix}_beats")
    print(f"[DEBUG] Number of beats in window: {num_beats}")

    # Classification với hình ảnh
    _, confidence, class_name = predict_single_beat_with_images(arr, sampling_rate=400, save_images=save_images, prefix=f"{prefix}_classification")
    class_name = map_lang(class_name)

    # Metrics HR/RR với hình ảnh
    cardiac_metrics = compute_cardiac_metrics_with_images(arr, fs, save_images, f"{prefix}_cardiac")

    # Tạo summary plot
    if save_images:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Signal with R-peaks
        time_axis = np.arange(len(arr)) / fs
        axes[0,0].plot(time_axis, arr, 'b-', linewidth=1)
        if len(peak_idxs) > 0:
            axes[0,0].plot(time_axis[peak_idxs], arr[peak_idxs], 'ro', markersize=6)
        axes[0,0].set_title(f'ECG Signal with R-peaks ({num_beats} beats)')
        axes[0,0].set_xlabel('Time (s)')
        axes[0,0].set_ylabel('Amplitude')
        axes[0,0].grid(True, alpha=0.3)
        
        # Classification result
        class_names = list(default_CLASS_MAPPING.values())
        # Dummy probabilities for visualization - in real case, get from prediction
        dummy_probs = [0.1, 0.1, 0.1, 0.1, 0.1]
        axes[0,1].bar(class_names, dummy_probs)
        axes[0,1].set_title(f'Prediction: {class_name} (Conf: {confidence:.3f})')
        axes[0,1].set_ylabel('Probability')
        
        # RR intervals
        if len(peak_idxs) > 1:
            rr_intervals = cardiac_metrics['rr_intervals']
            axes[1,0].plot(rr_intervals, 'go-', linewidth=1, markersize=4)
            axes[1,0].set_title(f'RR Intervals (HR: {cardiac_metrics["hr_mean"]:.1f} bpm)')
            axes[1,0].set_xlabel('Beat Index')
            axes[1,0].set_ylabel('RR Interval (s)')
            axes[1,0].grid(True, alpha=0.3)
        
        # Statistics
        stats_text = f"""Statistics:
Mean: {stats['mean']:.3f}
Std: {stats['std']:.3f}
Min: {stats['min']:.3f}
Max: {stats['max']:.3f}

Cardiac Metrics:
HR: {cardiac_metrics['hr_mean']:.1f} bpm
RR Mean: {cardiac_metrics['rr_mean']:.3f} s
RR Std: {cardiac_metrics['rr_std']:.3f} s
Beats: {num_beats}"""
        
        axes[1,1].text(0.1, 0.9, stats_text, transform=axes[1,1].transAxes,
                      verticalalignment='top', fontfamily='monospace',
                      bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        axes[1,1].set_xlim(0, 1)
        axes[1,1].set_ylim(0, 1)
        axes[1,1].axis('off')
        axes[1,1].set_title('Summary Statistics')
        
        plt.suptitle(f'ECG Window Analysis Summary - {class_name}')
        plt.tight_layout()
        
        filepath = IMAGES_DIR / f"{prefix}_summary.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[DEBUG] Saved analysis summary: {filepath}")

    return {
        'stats': stats,
        'class_name': class_name,
        'confidence': confidence,
        'cardiac_metrics': cardiac_metrics,
        'sampling_rate': fs,
        'num_beats': num_beats
    }