from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import io
import base64
from PIL import Image
from ultralytics import YOLO
from model.data_processing.ecg_analyse import predict_single_beat
from model.image_processing.predict_ct_liver_image import *

app = Flask(__name__)

# CORS setup
CORS(app, origins=[
    "https://bio-signal-processing.netlify.app",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

# Helpers
def image_to_base64(img) -> str:
    """
    Convert a NumPy array or PIL.Image to base64-encoded PNG string.
    """
    # If numpy array, convert to PIL
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Supported types & body parts
def _extract_supported():
    types = set(k[0] for k in MODEL_MAP.keys()) | set(k[0] for k in KERAS_MAP.keys())
    parts = set(k[1] for k in MODEL_MAP.keys()) | set(k[1] for k in KERAS_MAP.keys())
    return list(types), list(parts)

SUPPORTED_IMAGE_TYPES, SUPPORTED_BODY_PARTS = _extract_supported()

@app.route('/')
def index():
    return jsonify({'message': 'ECG and Image analysis server is running.'})

@app.route('/analyze_ecg', methods=['POST'])
def analyze_ecg():
    data = request.json or {}
    signal = data.get('signal', [])
    sampling_rate = data.get('sampling_rate', 400)

    if not signal:
        return jsonify({'error': 'No ECG signal provided'}), 400

    try:
        ecg_array = np.array(signal, dtype=float)
        predicted_class, confidence, class_name = predict_single_beat(ecg_array, sampling_rate)
        return jsonify({
            'predicted_class': int(predicted_class),
            'confidence': float(confidence),
            'class_name': class_name
        })
    except Exception as e:
        return jsonify({'error': 'ECG processing failed', 'details': str(e)}), 500

@app.route('/predict_image', methods=['POST'])
def predict_image():
    # Validate file & params
    print("Debug: Received request for image prediction.")
    if 'image' not in request.files:
        print("Debug: No image file provided.")
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    image_type = request.form.get('image_type')
    body_part = request.form.get('body_part')

    print(f"Debug: image_type={image_type}, body_part={body_part}")

    if image_type not in SUPPORTED_IMAGE_TYPES:
        print(f"Debug: Invalid image_type={image_type}. Must be one of {SUPPORTED_IMAGE_TYPES}.")
        return jsonify({'error': f'Invalid image_type. Must be one of {SUPPORTED_IMAGE_TYPES}'}), 400
    if body_part not in SUPPORTED_BODY_PARTS:
        print(f"Debug: Invalid body_part={body_part}. Must be one of {SUPPORTED_BODY_PARTS}.")
        return jsonify({'error': f'Invalid body_part. Must be one of {SUPPORTED_BODY_PARTS}'}), 400

    # Open and ensure RGB
    try:
        print("Debug: Attempting to open and convert image to RGB.")
        img = Image.open(image_file).convert('RGB')
    except Exception as e:
        print(f"Debug: Failed to open image file. Error: {str(e)}")
        return jsonify({'error': 'Invalid image file', 'details': str(e)}), 400

    key = (image_type, body_part)
    print(f"Debug: Key for model lookup: {key}")

    # YOLO path
    if key in MODEL_MAP:
        print(f"Debug: Found YOLO model for key={key}.")
        try:
            model = YOLO(MODEL_MAP[key])
            print("Debug: YOLO model loaded successfully.")
            result_np, detections = detect_objects(model, img)
            print(f"Debug: YOLO detections: {detections}")
            if not detections:
                print("Debug: No objects detected.")
                return jsonify({'error': 'No objects detected'}), 200
            result_b64 = image_to_base64(result_np)
            print("Debug: YOLO result image converted to base64.")
            return jsonify({'detections': detections, 'result_image': f'data:image/png;base64,{result_b64}'})
        except Exception as e:
            print(f"Debug: YOLO processing failed. Error: {str(e)}")
            return jsonify({'error': 'YOLO processing failed', 'details': str(e)}), 500

    # Keras segmentation path
    if key in KERAS_MAP:
        print(f"Debug: Found Keras model for key={key}.")
        try:
            mask_img = predict_ct_liver_mask(KERAS_MAP[key], img)
            print("Debug: Keras mask image generated successfully.")
            mask_b64 = image_to_base64(mask_img)
            print("Debug: Keras mask image converted to base64.")
            return jsonify({'mask_image': f'data:image/png;base64,{mask_b64}'})
        except Exception as e:
            print(f"Debug: Keras processing failed. Error: {str(e)}")
            return jsonify({'error': 'Keras processing failed', 'details': str(e)}), 500

    print(f"Debug: Unsupported combination: {image_type} - {body_part}.")
    return jsonify({'error': f'Unsupported combination: {image_type} - {body_part}'}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
