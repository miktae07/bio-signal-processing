#!/usr/bin/env python3

from sample_predict_ecg import predict_from_file

def main():
    # Đường dẫn file chứa dữ liệu ECG
    ecg_file = "ecg.txt"
    
    # Tần số lấy mẫu (Hz)
    sampling_rate = 400
    
    # File lưu kết quả (tùy chọn)
    output_file = "results/patient_001_results.txt"
    
    # Chạy dự đoán
    predict_from_file(ecg_file, sampling_rate, output_file)

if __name__ == "__main__":
    main()