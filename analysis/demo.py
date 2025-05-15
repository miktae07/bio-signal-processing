import streamlit as st
import json
import re
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, db

# Thiết lập cấu hình trang phải là lệnh Streamlit đầu tiên
st.set_page_config(page_title="Biosignal Dashboard", layout="wide")

# 1. Load credentials và init Firebase
firebase_json = st.secrets["FIREBASE_CREDENTIALS"]
cred = credentials.Certificate(json.loads(firebase_json))
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp32-9c871-default-rtdb.firebaseio.com/'
    })

# 2. Autorefresh mỗi 10 giây
st_autorefresh(interval=10_000, limit=None, key="firebase_refresh")

# 3. Đọc dữ liệu từ Firebase
data_ref = db.reference('/')
data = data_ref.get() or {}
if not data:
    st.warning("Chưa có giá trị nào được ghi vào cơ sở dữ liệu.")
    st.stop()

# 4. Hàm đệ quy parse nested dict thành records
def parse_node(sensor, node, path_keys):
    records = []
    if isinstance(node, dict):
        for k, v in node.items():
            records.extend(parse_node(sensor, v, path_keys + [k]))
    else:
        if len(path_keys) >= 6:
            try:
                ts_str = (
                    f"{path_keys[0]}-{path_keys[1].zfill(2)}-{path_keys[2].zfill(2)} "
                    f"{path_keys[3].zfill(2)}:{path_keys[4].zfill(2)}:{path_keys[5].zfill(2)}"
                )
                base_time = pd.to_datetime(ts_str)
            except Exception:
                return []
            if sensor == 'ECG':
                values = [int(v) for v in re.findall(r'-?\d+', str(node))]
                for idx, val in enumerate(values):
                    records.append({'sensor': sensor,
                                    'time': base_time + pd.to_timedelta(idx * 4, unit='ms'),
                                    'value': val})
            else:
                val = node
                try:
                    val = float(val)
                except Exception:
                    pass
                records.append({'sensor': sensor, 'time': base_time, 'value': val})
    return records

# 5. Tạo list records cho tất cả sensor
records = []
for sensor, readings in data.items():
    records.extend(parse_node(sensor, readings, []))

if not records:
    st.warning("Không có bản ghi hợp lệ để hiển thị.")
    st.stop()

# 6. DataFrame và nhóm theo sensor
DF = pd.DataFrame(records)
DF.sort_values(['sensor', 'time'], inplace=True)
sensor_groups = {s: g.set_index('time') for s, g in DF.groupby('sensor')}

# 7. Giao diện Streamlit
st.title("Biosignal Dashboard")

# Sidebar: chọn sensor và tham số phân tích
st.sidebar.header("Cấu hình")
selected = st.sidebar.multiselect("Lựa chọn sensor ", list(sensor_groups.keys()), list(sensor_groups.keys()))

# Phân tích dữ liệu
st.sidebar.subheader("Phân tích dữ liệu")
n = st.sidebar.number_input("Số lượng bản ghi cuối để phân tích", min_value=1, max_value=500, value=50)
do_analysis = st.sidebar.button("Chạy phân tích")

# 9. Hiển thị biểu đồ, bảng và phân tích
for s in selected:
    df_s = sensor_groups[s]
    # Tính margin cho trục Y
    y_min, y_max = df_s['value'].min(), df_s['value'].max()
    margin = (y_max - y_min) * 0.05 if y_max != y_min else (abs(y_max) * 0.1 or 1)
    domain = [y_min - margin, y_max + margin]

    st.subheader(f"Biểu đồ biến thiên {s}")
    chart = alt.Chart(df_s.reset_index()).mark_line().encode(
        x='time:T',
        y=alt.Y('value:Q', scale=alt.Scale(domain=domain))
    ).properties(height=300, width='container')
    st.altair_chart(chart, use_container_width=True)

    # Hiển thị trạng thái: đánh dấu nếu vượt ngưỡng (ví dụ trung bình ± 2*std)
    mean = df_s['value'].mean(); std = df_s['value'].std()
    latest = df_s['value'].iloc[-1]

    if st.button("🧪 Test trạng thái", key=f"test_status_{s}"):
        status = '🟡 Đang phân tích'
    else: 
        status = '🟢 Khỏe mạnh'

    st.markdown(f"**Trạng thái hiện tại**: {status}")
    st.subheader(f"Dữ liệu thô {s}")
    st.dataframe(df_s.reset_index().rename(columns={'index':'time'}), use_container_width=True)

    # Nếu yêu cầu phân tích
    if do_analysis:
        st.markdown(f"### Phân tích {s} (n={n})")
        last_n = df_s['value'].tail(n)
        st.write(f"- Giá trị trung bình: {last_n.mean():.2f}")
        st.write(f"- Giá trị cao nhất: {last_n.max():.2f}")
        st.write(f"- Giá trị thấp nhất: {last_n.min():.2f}")
        # Biểu đồ nhỏ cho phân tích
        small_chart = alt.Chart(last_n.reset_index()).mark_area(opacity=0.3).encode(
            x='time:T', y='value:Q'
        ).properties(height=150)
        st.altair_chart(small_chart, use_container_width=True)
