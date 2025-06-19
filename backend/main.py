#!/usr/bin/env python3
from model.sample.sample_predict_ecg import test_single_beat, test_window_analysis

if __name__ == "__main__":
    file_path = "/home/ubuntu/bio-signal-processing/backend/model/sample/ecg_data.txt"
    test_single_beat(file_path)
    test_window_analysis(file_path)