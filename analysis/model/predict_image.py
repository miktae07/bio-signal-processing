from ultralytics import YOLO
from PIL import Image

# Load mô hình YOLOv8 một lần khi import
model = YOLO("yolov8n.pt")

def detect_objects(image: Image.Image):
    """
    Hàm dự đoán đối tượng trong ảnh với YOLOv8
    Trả về:
        - ảnh numpy có bounding boxes
        - danh sách label + độ tin cậy
    """
    results = model(image)

    if not results:
        return None, []

    result_img = results[0].plot()  # ảnh với bounding boxes
    detections = []

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = results[0].names[cls_id]
        detections.append((label, conf))

    return result_img, detections
