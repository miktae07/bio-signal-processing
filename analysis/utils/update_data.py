import time
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import os
from google.auth.exceptions import RefreshError
from .firebase_utils import parse_node

# Cấu hình Firebase
SERVICE_ACCOUNT_PATH = 'esp32-9c871-firebase-adminsdk-fbsvc-ec6b1a3d27.json'
DATABASE_URL = 'https://esp32-9c871-default-rtdb.firebaseio.com/'

# Khởi Firebase toàn cục
def init_firebase(force_reinit=False):
    global firebase_admin
    # Nếu đã init và không cần reinit, bỏ qua
    if firebase_admin._apps and not force_reinit:
        return
    # Nếu cần reinit, xoá app cũ
    if firebase_admin._apps and force_reinit:
        for name, app in list(firebase_admin._apps.items()):
            firebase_admin.delete_app(app)
    # Init nếu chưa có
    if not firebase_admin._apps:
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            raise FileNotFoundError(f"Credential file not found: {SERVICE_ACCOUNT_PATH}")
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, { 'databaseURL': DATABASE_URL })
        print(f"✅ Firebase initialized with {SERVICE_ACCOUNT_PATH}")

# Hàm lấy snapshot toàn bộ sensor groups
def get_sensor_groups(debug=False):
    init_firebase()
    try:
        raw = db.reference('/').get() or {}
    except Exception as e:
        print(f"🔴 Lỗi khi lấy dữ liệu: {e}")
        return {}
    if not isinstance(raw, dict):
        print(f"🔴 Dữ liệu không hợp lệ: {type(raw)}")
        return {}
    # parse với hàm parse_node đã định nghĩa ở module firebase_utils
    
    records = []
    for sensor, node in raw.items():
        recs = parse_node(sensor, node, [])
        if recs:
            records.extend(recs)
    if not records:
        return {}
    df = pd.DataFrame(records)
    if 'sensor' not in df.columns or 'time' not in df.columns:
        return {}
    df.sort_values(['sensor','time'], inplace=True)
    grouped = {name: g.set_index('time') for name, g in df.groupby('sensor')}
    return grouped

# Hàm mẫu xử lý sự kiện thay đổi
def on_change(sensor, df):
    print(f"🔔 Event on sensor {sensor}: {len(df)} records")
    print(df)

# Hàm khởi listener
def start_sensor_listener(on_change, debug=True):
    """
    Khởi listener theo dõi realtime thay đổi tại gốc Firebase.
    Gọi on_change(sensor_name, df) khi có event.
    Trả về ListenerRegistration (call .close() để dừng).
    """
    if not callable(on_change):
        raise ValueError('on_change phải là callable')
    init_firebase()
    def _callback(event):
        parts = event.path.strip('/').split('/')
        sensor = parts[0] if parts and parts[0] else None
        if debug:
            print(f"📡 Event type={event.event_type} on sensor={sensor}")
        if sensor:
            groups = get_sensor_groups(debug=debug)
            df = groups.get(sensor, pd.DataFrame())
            on_change(sensor, df)
    listener = db.reference('/').listen(_callback)
    if debug:
        print('✅ Firebase listener started')
    return listener

if __name__ == "__main__":
    # Khởi Firebase và in trạng thái ban đầu
    try:
        init_firebase()
    except Exception as e:
        print(f"🔴 init_firebase failed: {e}")
        exit(1)
    sensor_groups = get_sensor_groups(debug=True)
    print("🚀 Initial sensor groups:")
    for s, df in sensor_groups.items():
        print(f"- {s}: {len(df)} records")
    listener = start_sensor_listener(on_change, debug=True)
    print("Nhấn Ctrl+C để dừng listener...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🚫 Stopping listener...")
        listener.close()
        print("✅ Listener stopped.")
