from ultralytics import YOLO
from PIL import Image
import numpy as np

def detect_objects(model_path: str, image: Image.Image):
    """
    Load YOLO model (custom or default), perform object detection, and return
    the plotted image (NumPy array) and a list of detections (label, confidence).

    Args:
        model_path (str): path to YOLO weights or 'yolov8n.pt' for default Nano model
        image (PIL.Image): input image

    Returns:
        Tuple[np.ndarray, List[Tuple[str, float]]]: (result_image_np, detections_list)
    """
    # Load model (will download default if 'yolov8n.pt' not found locally)
    model = YOLO(model_path)

    # Run inference
    results = model(image)
    if not results or len(results) == 0 or not hasattr(results[0], 'boxes'):
        return None, []

    # Plot results on image (returns NumPy array)
    result_np = results[0].plot()

    # Extract detections (label and confidence)
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = results[0].names[cls_id]
        conf = float(box.conf[0])
        detections.append((label, conf))

    return result_np, detections
