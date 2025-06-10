from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import io
import base64
from ultralytics import YOLO
from model.data_processing.ecg_analyse import predict_single_beat
from model.image_processing.predict_image import detect_objects, predict_ct_liver_mask, MODEL_MAP, KERAS_MAP

app = Flask(__name__)

CORS(app, origins=[
    "https://bio-signal-processing.netlify.app",  # production
    "http://127.0.0.1:5500",                      # local bằng 127.0.0.1
    "http://localhost:5500"                       # local bằng localhost
])

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

@app.route('/predict_image', methods=['POST'])
def predict_image():
    try:
        # Validate input
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        if 'image_type' not in request.form or 'body_part' not in request.form:
            return jsonify({'error': 'Missing image_type or body_part'}), 400

        image_file = request.files['image']
        image_type = request.form['image_type']
        body_part = request.form['body_part']

        # Validate image_type and body_part
        if image_type not in SUPPORTED_IMAGE_TYPES:
            return jsonify({'error': f'Invalid image_type. Must be one of {SUPPORTED_IMAGE_TYPES}'}), 400
        if body_part not in SUPPORTED_BODY_PARTS:
            return jsonify({'error': f'Invalid body_part. Must be one of {SUPPORTED_BODY_PARTS}'}), 400

        # Open image with PIL
        try:
            image = Image.open(image_file)
            if image.mode != "RGB":
                image = image.convert("RGB")
        except Exception as e:
            return jsonify({'error': 'Invalid image file', 'details': str(e)}), 400

        # Select model based on image_type and body_part
        model_key = (image_type, body_part)
        if model_key in MODEL_MAP:
            # YOLO model processing
            model_path = MODEL_MAP[model_key]
            try:
                model = YOLO(model_path)
            except Exception as e:
                return jsonify({'error': 'Failed to load YOLO model', 'details': str(e)}), 500

            result_img, detections = detect_objects(model, image)
            if result_img is None or not detections:
                return jsonify({'error': 'No objects detected'}), 200

            # Convert result image to base64
            result_base64 = image_to_base64(result_img)
            return jsonify({
                'detections': detections,  # List of (label, confidence)
                'result_image': f'data:image/png;base64,{result_base64}'
            })

        elif model_key in KERAS_MAP:
            # Keras model processing (e.g., CT Liver segmentation)
            model_path = KERAS_MAP[model_key]
            try:
                mask_img = predict_ct_liver_mask(model_path, image)
            except Exception as e:
                return jsonify({'error': 'Failed to process Keras model', 'details': str(e)}), 500

            # Convert mask image to base64
            mask_base64 = image_to_base64(mask_img)
            return jsonify({
                'mask_image': f'data:image/png;base64,{mask_base64}'
            })

        else:
            return jsonify({'error': f'Unsupported combination: {image_type} - {body_part}'}), 400

    except Exception as e:
        return jsonify({'error': 'Failed to process image', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
