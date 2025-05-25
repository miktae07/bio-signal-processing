import numpy as np
from tensorflow.keras.models import load_model

# Mapping classes
CLASS_MAPPING = {
    0: 'N',  # Non-ecotic beats (normal beat)
    1: 'S',  # Supraventricular ectopic beats
    2: 'V',  # Ventricular ectopic beats
    3: 'F',  # Fusion Beats
    4: 'Q'   # Unknown Beats
}

def predict_ecg(input_signal):
    """
    Dự đoán kết quả từ tín hiệu ECG đầu vào
    Args:
        input_signal: numpy array có 500 giá trị
    Returns:
        predicted_class: lớp dự đoán
        confidence: độ tin cậy của dự đoán
        class_name: tên lớp dự đoán
    """
    # Load model đã train
    model = load_model('analysis/data_processing/best_model.h5')
    
    # Chuyển về số dương bằng cách lấy giá trị tuyệt đối
    input_signal = np.abs(input_signal)
    
    # Lấy điểm và reshape
    # input_len = len(input_signal)
    input_data = input_signal[:186].reshape(1, 186, 1)
    
    # Dự đoán
    predictions = model.predict(input_data)
    
    # Lấy kết quả dự đoán
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0])
    class_name = CLASS_MAPPING[predicted_class]
    
    return predicted_class, confidence, class_name

# Example usage:
input_signal = np.array([7.77E-01, 7.04E-01, 6.04E-01, 5.08E-01, 3.79E-01, 2.64E-01, 1.55E-01, 9.22E-02, 3.23E-02, 3.53E-02, 5.68E-02, 1.06E-01, 2.06E-01, 3.32E-01, 3.66E-01, 4.22E-01, 4.78E-01, 5.55E-01, 6.10E-01, 6.51E-01, 6.53E-01, 6.73E-01, 6.73E-01, 6.80E-01, 6.84E-01, 6.88E-01, 6.96E-01, 7.22E-01, 7.20E-01, 7.37E-01, 7.48E-01, 7.71E-01, 7.77E-01, 8.00E-01, 8.13E-01, 8.33E-01, 8.46E-01, 8.74E-01, 8.91E-01, 9.00E-01, 8.99E-01, 9.11E-01, 9.08E-01, 9.06E-01, 8.74E-01, 8.48E-01, 8.17E-01, 7.93E-01, 7.54E-01, 7.22E-01, 6.85E-01, 6.62E-01, 6.28E-01, 6.24E-01, 6.10E-01, 6.07E-01, 5.81E-01, 5.90E-01, 5.78E-01, 5.91E-01, 5.82E-01, 5.82E-01, 5.67E-01, 5.76E-01, 5.68E-01, 5.85E-01, 5.71E-01, 5.79E-01, 5.73E-01, 5.76E-01, 5.61E-01, 5.68E-01, 5.64E-01, 5.68E-01, 5.64E-01, 5.68E-01, 5.59E-01, 5.58E-01, 5.33E-01, 5.55E-01, 5.58E-01, 5.55E-01, 5.51E-01, 5.51E-01, 5.48E-01, 5.56E-01, 5.44E-01, 5.55E-01, 5.50E-01, 5.53E-01, 5.42E-01, 5.56E-01, 5.47E-01, 5.56E-01, 5.41E-01, 5.48E-01, 5.55E-01, 5.71E-01, 5.81E-01, 6.82E-01, 1.00E+00, 9.19E-01, 8.45E-01, 7.73E-01, 6.56E-01, 5.53E-01, 4.29E-01, 3.06E-01, 1.61E-01, 8.60E-02, 0.00E+00, 0.00E+00, 2.46E-02, 9.98E-02, 2.01E-01, 3.29E-01, 3.81E-01, 4.50E-01, 5.04E-01, 5.73E-01, 6.22E-01, 6.56E-01, 6.68E-01, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00, 0.00E+00
])  # Paste mảng 500 giá trị vào đây
predicted_class, confidence, class_name = predict_ecg(input_signal)
print(f"Predicted class number: {predicted_class}")
print(f"Predicted class name: {class_name}")
print(f"Confidence: {confidence:.2f}")
print("\nClass Mapping:")
print("0 - N: Non-ecotic beats (normal beat)")
print("1 - S: Supraventricular ectopic beats")
print("2 - V: Ventricular ectopic beats")
print("3 - F: Fusion Beats")
print("4 - Q: Unknown Beats")

