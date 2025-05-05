import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import pandas as pd
import json

# Đường dẫn tới file JSON key
# key_path = os.environ.get("FIREBASE_KEY_PATH")
# print("Firebase key path:", key_path)  # kiểm tra in ra đường dẫn
firebase_json = st.secrets["FIREBASE_CREDENTIALS"]
cred_dict = json.loads(firebase_json)

cred = credentials.Certificate(cred_dict)
# Chỉ initialize nếu chưa có default app
# try:
#     firebase_admin.get_app()
# except ValueError:

# 2. Xoá app mặc định (nếu đã tồn tại)
try:
    default_app = firebase_admin.get_app()
    firebase_admin.delete_app(default_app)
except ValueError:
    # nếu chưa có app nào thì bỏ qua
    pass

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp32-9c871-default-rtdb.firebaseio.com/'  # thay bằng URL Realtime DB của bạn
})

ref_sensors      = db.reference('sensors')
ref_measurements = db.reference('measurements')
sensors = ['ECG', 'EEG', 'SpO2', 'TEMP']

# 3. Lấy metadata (nếu cần)
metadata = {s: ref_sensors.child(s).get() for s in sensors}

# 4. Lấy measurements, gom vào DataFrame
records = []

# 2. Tham chiếu
for s in sensors:
    data = ref_measurements.child(s).get() or {}
    for ts, val in data.items():
        records.append({
            'sensor': s,
            'time': pd.to_datetime(ts),
            'value': val
        })

df = pd.DataFrame(records)
df.sort_values(['sensor','time'], inplace=True)

# 5. Hiển thị giá trị thô
df

# Tiêu đề chung
st.title("Biosignal Dashboard")

# 1. Hiển thị Metadata của các sensor
st.header("Sensor Metadata")
for sensor, props in metadata.items():
    st.subheader(sensor)
    st.json(props)

# 2. Hiển thị bảng dữ liệu thô
st.header("Raw Measurements")
st.dataframe(df, use_container_width=True)  # :contentReference[oaicite:0]{index=0}

# 3. Chuẩn bị pivot table cho biểu đồ
pivot = df.pivot(index="time", columns="sensor", values="value")

# 4. Vẽ biểu đồ time-series cho tất cả sensors
st.header("Time Series Chart")
st.line_chart(pivot, use_container_width=True)  # :contentReference[oaicite:1]{index=1}