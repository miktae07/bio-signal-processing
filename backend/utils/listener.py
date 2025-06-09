"""
firebase_listener.py

Script đơn giản cố định file service account và URL để lắng nghe mọi thay đổi trên Firebase Realtime Database
"""
import json
import firebase_admin
from firebase_admin import credentials, db

# Cấu hình cố định
SERVICE_ACCOUNT = 'esp32-9c871-firebase-adminsdk-fbsvc-ec6b1a3d27.json'
DATABASE_URL = 'https://esp32-9c871-default-rtdb.firebaseio.com/'

# Khởi tạo Firebase Admin SDK
cred = credentials.Certificate(SERVICE_ACCOUNT)
firebase_admin.initialize_app(cred, { 'databaseURL': DATABASE_URL })
print(f"🔌 Listening for changes at {DATABASE_URL}")

# Tham chiếu đến gốc database
ref = db.reference('/')

# Callback khi có event
def listener(event):
    print('--- Firebase Event ---')
    print(f"Type:  {event.event_type}")
    print(f"Path:  {event.path}")
    print(f"Data:  {json.dumps(event.data, ensure_ascii=False)}")
    print('----------------------')

# Bắt listener
stream = ref.listen(listener)

# Giữ script chạy vô hạn
try:
    print("Nhấn Ctrl+C để dừng listener.")
    while True:
        pass
except KeyboardInterrupt:
    print("🚫 Stopping listener...")
    stream.close()
    print("✅ Listener stopped.")
