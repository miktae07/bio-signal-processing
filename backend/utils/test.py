import os
import firebase_admin
from firebase_admin import credentials, db

# 1. Xác định đường dẫn đến JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))    # folder "analysis"
cred_path = os.path.join(BASE_DIR, "esp32-9c871-firebase-adminsdk-fbsvc-ec6b1a3d27.json")
cred_path = os.path.normpath(cred_path)

print("DEBUG: cred_path =", cred_path, "; exists:", os.path.isfile(cred_path))

# 2. Thử initialize
try:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://esp32-9c871-default-rtdb.firebaseio.com/"
    })
    print("✅ Firebase initialize_app thành công")
except Exception as e:
    print("❌ Lỗi khi initialize Firebase:", e)
    exit(1)

# 3. Thử đọc 1 node bất kỳ
try:
    ref = db.reference("/")
    data = ref.get()
    print("Dữ liệu tại '/':", data)
except Exception as e:
    print("❌ Lỗi khi gọi ref.get():", e)
