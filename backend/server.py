
# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import io
import base64
from PIL import Image
from ultralytics import YOLO

# import model maps and functions from predict_image module
from model.data_processing.ecg_analyse import predict_single_beat
from model.image_processing.predict_ct_liver_image import *

app = Flask(__name__)
CORS(app, origins="*")

# Helpers
def image_to_base64(img) -> str:
    print("Debug: Converting image to base64...")
    if isinstance(img, np.ndarray):
        print("Debug: Image is NumPy array, converting to PIL.")
        img = Image.fromarray(img)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    print("Debug: Image saved to buffer as PNG.")
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Supported types & body parts
def _extract_supported():
    print("Debug: Extracting supported image types and body parts from model maps.")
    types = set(k[0] for k in MODEL_MAP.keys()) | set(k[0] for k in KERAS_MAP.keys())
    parts = set(k[1] for k in MODEL_MAP.keys()) | set(k[1] for k in KERAS_MAP.keys())
    print(f"Debug: Supported image types: {types}")
    print(f"Debug: Supported body parts: {parts}")
    return list(types), list(parts)

SUPPORTED_IMAGE_TYPES, SUPPORTED_BODY_PARTS = _extract_supported()

@app.route('/')
def index():
    print("Debug: Health check route called.")
    return jsonify({'message': 'ECG and Image analysis server is running.'})

@app.route('/analyze_ecg', methods=['POST'])
def analyze_ecg():
    print("Debug: Received ECG analysis request.")
    data = request.get_json(force=True) or {}
    signal = data.get('signal', [])
    sampling_rate = data.get('sampling_rate', 400)
    print(f"Debug: Signal length = {len(signal)}, Sampling rate = {sampling_rate}")

    if not signal:
        print("Debug: No signal data provided.")
        return jsonify({'error': 'No ECG signal provided'}), 400

    try:
        ecg_array = np.array(signal, dtype=float)
        print(f"Debug: ECG array shape: {ecg_array.shape}, dtype: {ecg_array.dtype}")
        predicted_class, confidence, class_name = predict_single_beat(ecg_array, sampling_rate)
        print(f"Debug: ECG predicted class = {predicted_class}, confidence = {confidence}, label = {class_name}")
        return jsonify({
            'predicted_class': int(predicted_class),
            'confidence': float(confidence),
            'class_name': class_name
        })
    except Exception as e:
        print(f"Debug: ECG processing failed. Error: {e}")
        return jsonify({'error': 'ECG processing failed', 'details': str(e)}), 500

@app.route('/predict_image', methods=['POST'])
def predict_image():
    print("Debug: Received request for image prediction.")
    if 'image' not in request.files:
        print("Debug: No image file provided in request.")
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    image_type = request.form.get('image_type')
    body_part = request.form.get('body_part')
    print(f"Debug: image_type={image_type}, body_part={body_part}")

    if image_type not in SUPPORTED_IMAGE_TYPES:
        print(f"Debug: Unsupported image_type={image_type}")
        return jsonify({'error': f'Invalid image_type. Must be one of {SUPPORTED_IMAGE_TYPES}'}), 400
    if body_part not in SUPPORTED_BODY_PARTS:
        print(f"Debug: Unsupported body_part={body_part}")
        return jsonify({'error': f'Invalid body_part. Must be one of {SUPPORTED_BODY_PARTS}'}), 400

    try:
        print("Debug: Attempting to open uploaded image...")
        img = Image.open(image_file)
        print(f"Debug: Original image mode: {img.mode}")
        img = img.convert('RGB')
        print("Debug: Image converted to RGB.")
    except Exception as e:
        print(f"Debug: Failed to open/convert image. Error: {e}")
        return jsonify({'error': 'Invalid image file', 'details': str(e)}), 400

    key = (image_type, body_part)
    print(f"Debug: Model lookup key: {key}")

    # YOLO path
    if key in MODEL_MAP:
        print("Debug: Matching YOLO model found.")
        try:
            model = YOLO_MODELS[key]
            result_np, detections = detect_objects(model, img)
            print(f"Debug: Detections = {detections}")
            if not detections:
                print("Debug: No objects detected.")
                return jsonify({'error': 'No objects detected'}), 200
            result_b64 = image_to_base64(result_np)
            print("Debug: Result image converted to base64.")
            return jsonify({'detections': detections, 'result_image': f'data:image/png;base64,{result_b64}'})
        except Exception as e:
            print(f"Debug: YOLO inference failed. Error: {e}")
            return jsonify({'error': 'YOLO processing failed', 'details': str(e)}), 500

    # Keras path
    if key in KERAS_MAP:
        print("Debug: Matching Keras model found.")
        try:
            mask_img = predict_ct_liver_mask(img)
            print("Debug: Mask generated by Keras model.")
            mask_b64 = image_to_base64(mask_img)
            print("Debug: Mask image converted to base64.")
            return jsonify({'mask_image': f'data:image/png;base64,{mask_b64}'})
        except Exception as e:
            print(f"Debug: Keras segmentation failed. Error: {e}")
            return jsonify({'error': 'Keras processing failed', 'details': str(e)}), 500

    print(f"Debug: No model found for combination: {key}")
    return jsonify({'error': f'Unsupported combination: {image_type} - {body_part}'}), 400

if __name__ == '__main__':
    print("Debug: Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
