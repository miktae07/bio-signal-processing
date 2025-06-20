#!/usr/bin/env python3
"""
Sample script to predict ECG signal from CSV file using trained model
Each row represents 1 heartbeat, and the last value is the expected label
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

# Import your ECG analysis functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.data_processing.ecg_analyse import predict_ecg_with_images as predict_ecg, predict_single_beat_with_images as predict_single_beat, CLASS_MAPPING

def read_ecg_from_csv(file_path, row_numbers=None):
    """
    Read ECG signal from CSV file. Each row is a heartbeat, last value is expected label
    
    Args:
        file_path: path to the CSV file
        row_numbers: list of row indices to read (starting from 0), None to read all
    
    Returns:
        tuple: (ecg_signals, expected_labels)
    """
    try:
        print(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path, header=None)

        if row_numbers is not None:
            df = df.iloc[row_numbers]

        ecg_signals = []
        expected_labels = []

        for _, row in df.iterrows():
            ecg_data = row.values[:-1].astype(float)
            raw_label = row.values[-1]

            # Convert label (e.g., 0.0) to class name (e.g., 'N')
            try:
                int_label = int(float(raw_label))
                label = CLASS_MAPPING.get(int_label, 'Q')
            except:
                label = 'Q'

            ecg_signals.append(ecg_data)
            expected_labels.append(label)

        print(f"Successfully loaded {len(ecg_signals)} heartbeats from CSV.")
        print(f"First 5 labels: {expected_labels[:5]}")

        return ecg_signals, expected_labels

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None, None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None, None

def predict_from_csv(file_path, sampling_rate=400, row_numbers=None, output_file=None):
    """
    Predict ECG signals from CSV file
    
    Args:
        file_path: path to the CSV file
        sampling_rate: signal sampling rate in Hz
        row_numbers: list of row indices to read (None to read all)
        output_file: optional output file to save prediction results
    """
    print("=" * 60)
    print("ECG SIGNAL PREDICTION FROM CSV")
    print("=" * 60)

    ecg_signals, expected_labels = read_ecg_from_csv(file_path, row_numbers)
    if ecg_signals is None:
        return

    print(f"\nInput Information:")
    print(f"- File: {file_path}")
    if row_numbers:
        print(f"- Selected rows: {row_numbers}")
    print(f"- Total beats: {len(ecg_signals)}")
    print(f"- Sampling rate: {sampling_rate} Hz")

    print("\n" + "=" * 60)
    print("PREDICTING...")
    print("=" * 60)

    try:
        all_results = []

        for i, (ecg_signal, expected_label) in enumerate(zip(ecg_signals, expected_labels)):
            print(f"\nAnalyzing beat {i} (Expected label: {expected_label})")

            predicted_class, confidence, class_name = predict_single_beat(ecg_signal, sampling_rate)

            result = {
                'beat_index': i,
                'ecg_signal': ecg_signal,
                'expected_label': expected_label,
                'predicted_class': predicted_class,
                'class_name': class_name,
                'confidence': confidence,
                'is_correct': (class_name == expected_label)
            }
            all_results.append(result)

            print(f"    Expected label: {expected_label}")
            print(f"    Predicted class: {class_name}")
            print(f"    Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
            print(f"    {'CORRECT' if result['is_correct'] else 'INCORRECT'}")

        correct_predictions = sum(1 for r in all_results if r['is_correct'])
        accuracy = correct_predictions / len(all_results)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total beats: {len(all_results)}")
        print(f"Correct predictions: {correct_predictions}")
        print(f"Accuracy: {accuracy:.2f} ({accuracy*100:.1f}%)")

        if output_file:
            save_results_to_file(all_results, output_file, file_path, sampling_rate)

    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()

def save_results_to_file(results, output_file, input_file, sampling_rate):
    """
    Save prediction results to output file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ECG PREDICTION RESULTS FROM CSV\n")
            f.write("=" * 50 + "\n")
            f.write(f"Input file: {input_file}\n")
            f.write(f"Sampling rate: {sampling_rate} Hz\n")
            f.write(f"Number of beats analyzed: {len(results)}\n\n")

            correct = sum(1 for r in results if r['is_correct'])
            accuracy = correct / len(results)

            f.write(f"SUMMARY:\n")
            f.write(f"Correct predictions: {correct}/{len(results)}\n")
            f.write(f"Accuracy: {accuracy:.4f}\n\n")

            f.write("DETAILED RESULTS:\n")
            for result in results:
                f.write(f"\nBeat {result['beat_index']}:\n")
                f.write(f"  Expected label: {result['expected_label']}\n")
                f.write(f"  Predicted class: {result['predicted_class']} ({result['class_name']})\n")
                f.write(f"  Confidence: {result['confidence']:.3f}\n")
                f.write(f"  Result: {'CORRECT' if result['is_correct'] else 'INCORRECT'}\n")
                f.write(f"  Signal length: {len(result['ecg_signal'])} points\n")

        print(f" Results saved to: {output_file}")

    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "mitbih_test.csv")

    predict_from_csv(csv_file, sampling_rate=187, row_numbers=[0, 5, 10, 20122, 20123, 18674, 18675, 18118, 18119, 21871])
