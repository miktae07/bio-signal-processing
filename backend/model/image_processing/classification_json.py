# modelderm_retry.py

import os
import sys
import time
import cv2
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Các endpoint của ModelDerm
URLS = [
    "https://t.modelderm.com/api?json_format=1",
    "https://t1.modelderm.com/api?json_format=1",
    "https://t2.modelderm.com/api?json_format=1",
]

def setup_session(retries=3, backoff_factor=1):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[502, 503, 504],
        allowed_methods=frozenset(['POST', 'GET'])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

def get_center_square(img):
    h, w = img.shape[:2]
    if w > h:
        dx = (w - h) // 2
        return img[:, dx:dx+h]
    else:
        dy = (h - w) // 2
        return img[dy:dy+w, :]

def diagnose(image_path):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Không tìm thấy file: {image_path}")

    img = cv2.imread(image_path, cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    if img is None:
        raise ValueError("Không đọc được ảnh hoặc định dạng không hỗ trợ")

    crop = get_center_square(img)
    ret, enc = cv2.imencode(".webp", crop)
    if not ret:
        raise RuntimeError("Encode ảnh thất bại")

    files = {'file': (os.path.basename(image_path), enc.tobytes(), 'image/webp')}
    session = setup_session(retries=3, backoff_factor=2)

    last_exc = None
    for url in URLS:
        print(f"Thử endpoint: {url}")
        try:
            resp = session.post(url, files=files, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            preds = data.get("predictions", [])
            if not preds:
                print(f"[{url}] Không có kết quả dự đoán trả về")
                continue
            return sorted(preds, key=lambda x: x['probability'], reverse=True)
        except Exception as e:
            print(f"[{url}] Lỗi: {e}")
            last_exc = e
            time.sleep(2)  # delay trước khi chuyển endpoint

    raise RuntimeError("Các endpoint ModelDerm đều thất bại") from last_exc

if __name__ == "__main__":
    img = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    try:
        preds = diagnose(img)
    except Exception as e:
        print(f"💥 Chẩn đoán thất bại: {e}")
        sys.exit(1)

    print("✅ Kết quả chẩn đoán (Top 5):")
    for p in preds[:5]:
        name = p.get('class_name', 'Unknown')
        prob = p.get('probability', 0) * 100
        print(f" - {name}: {prob:.2f}%")
