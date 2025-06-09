from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from model.data_processing.ecg_analyse import predict_single_beat

app = Flask(__name__)
CORS(app)  # ✅ Bật CORS để cho phép gọi từ JS frontend

@app.route('/')
def index():
    return jsonify({'message': 'ECG analysis server is running.'})

@app.route('/analyze_ecg', methods=['POST'])
def analyze_ecg():
    data = request.json
    print("📥 Dữ liệu nhận được:", data)

    signal = data.get('signal', [])
    sampling_rate = data.get('sampling_rate', 400)

    if not signal:
        print("⚠️ Không có tín hiệu ECG được gửi!")
        return jsonify({'error': 'No ECG signal provided'}), 400

    try:
        ecg_array = np.array(signal, dtype=float)
        print("ECG array shape:", ecg_array.shape, "dtype:", ecg_array.dtype)
        predicted_class, confidence, class_name = predict_single_beat(ecg_array, sampling_rate)

        print("✅ Dự đoán thành công:")
        print(f"Class: {predicted_class}, Name: {class_name}, Confidence: {confidence:.2f}")

        return jsonify({
            'predicted_class': int(predicted_class),
            'confidence': float(confidence),
            'class_name': class_name
        })
    except Exception as e:
        print("❌ Lỗi xử lý:", str(e))
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
