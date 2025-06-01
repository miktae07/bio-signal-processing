# utils/firebase_utils.py

import json
import re
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import os
from google.auth.exceptions import RefreshError

def parse_node(sensor, node, path_keys):
    records = []
    if isinstance(node, dict):
        for k, v in node.items():
            records.extend(parse_node(sensor, v, path_keys + [k]))
    else:
        if len(path_keys) >= 6:
            try:
                ts = (f"{path_keys[0]}-{path_keys[1].zfill(2)}-{path_keys[2].zfill(2)} "
                      f"{path_keys[3].zfill(2)}:{path_keys[4].zfill(2)}:{path_keys[5].zfill(2)}")
                base_time = pd.to_datetime(ts)
            except:
                return []
            if sensor == 'ECG':
                vals = [int(v) for v in re.findall(r'-?\d+', str(node))]
                for i, v in enumerate(vals):
                    records.append({
                        'sensor': sensor,
                        'time': base_time + pd.to_timedelta(i * 4, unit='ms'),
                        'value': v
                    })
            else:
                try:
                    val = float(node)
                except:
                    val = node
                records.append({'sensor': sensor, 'time': base_time, 'value': val})
    return records

def init_firebase(force_reinit=False):
    """
    Khởi tạo Firebase Admin SDK. Nếu force_reinit=True, xóa app cũ rồi init lại.
    Chỉ sử dụng print để debug, không dùng Streamlit.
    """

    # Nếu đã có app và không cần reinit, bỏ qua
    if firebase_admin._apps and not force_reinit:
        print("DEBUG: Firebase đã được khởi rồi, bỏ qua init.")
        return

    # Nếu đã có app nhưng cần reinit, xóa hết
    if firebase_admin._apps and force_reinit:
        print("DEBUG: Xóa app cũ để re-init Firebase...")
        for name, app in list(firebase_admin._apps.items()):
            try:
                firebase_admin.delete_app(app)
                print(f"DEBUG: Đã xóa app '{name}'.")
            except Exception as e:
                print(f"⚠️ Không thể xóa app '{name}': {e}")

    # Xác định đường dẫn tới file JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cred_filename = "esp32-9c871-firebase-adminsdk-fbsvc-ec6b1a3d27.json"
    cred_path = os.path.normpath(os.path.join(BASE_DIR, cred_filename))

    # Kiểm tra tồn tại file
    if not os.path.isfile(cred_path):
        print(f"❌ Không tìm thấy file credential JSON tại: {cred_path}")
        raise FileNotFoundError(f"Credential JSON không tồn tại: {cred_path}")

    # Đọc raw JSON để debug (chỉ in 200 ký tự đầu)
    try:
        with open(cred_path, "r", encoding="utf-8") as f:
            raw_json = f.read()
    except Exception as e:
        print(f"🔴 Lỗi khi đọc file JSON: {e}")
        raise

    snippet = raw_json[:200].replace("\n", "\\n")
    print(f"DEBUG: 200 ký tự đầu của JSON: {snippet} …")

    # Parse JSON thử
    try:
        config = json.loads(raw_json)
    except Exception as e:
        print(f"🔴 Lỗi khi json.loads: {e}")
        raise

    # In ra các key để kiểm tra
    if isinstance(config, dict):
        print(f"DEBUG: Các key trong config JSON: {list(config.keys())}")
    else:
        print(f"🔴 Nội dung credential không phải dict mà là {type(config)}")
        raise TypeError("Credential JSON không phải dict")

    # Khởi tạo Firebase Admin SDK
    try:
        cred = credentials.Certificate(config)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://esp32-9c871-default-rtdb.firebaseio.com/"
        })
        print("✅ Firebase initialized successfully!")
    except Exception as e:
        print(f"🔴 Lỗi khi initialize Firebase Admin SDK: {e}")
        raise

def get_sensor_groups():
    """
    1. Gọi init_firebase(). Nếu JWT invalid, xóa app cũ và thử lại.
    2. Lấy data từ node gốc "/".
    3. Parse từng node con, lưu vào records.
    4. Tạo DataFrame, sắp xếp, group theo 'sensor'.
    5. Trả về dict {sensor: DataFrame_index_time}.
    Chỉ sử dụng print để debug.
    """

    # 1. Khởi Firebase lần đầu
    try:
        init_firebase()
    except Exception as e:
        print(f"🔴 init_firebase() lần 1 failed: {e}")
        return {}

    # 2. Lấy data gốc, nếu gặp invalid_grant thì force reinit và thử lại
    try:
        data_ref = db.reference("/")
        data = data_ref.get()
    except Exception as e:
        err_str = str(e)
        if "invalid_grant" in err_str or isinstance(e, RefreshError):
            print("⚠️ Phát hiện 'Invalid JWT Signature'. Xóa app cũ và thử re-init...")
            try:
                init_firebase(force_reinit=True)
            except Exception as e2:
                print(f"🔴 init_firebase(force_reinit) failed: {e2}")
                return {}

            # Thử lấy lại data một lần nữa
            try:
                data_ref = db.reference("/")
                data = data_ref.get()
            except Exception as e3:
                print(f"🔴 Lỗi khi gọi data_ref.get() sau re-init: {e3}")
                return {}
        else:
            print(f"🔴 Lỗi khi gọi data_ref.get(): {e}")
            return {}

    # 3. Kiểm tra data
    if data is None:
        print("⚠️ Firebase trả về None cho node '/'.")
        return {}
    if not isinstance(data, dict):
        print(f"🔴 Dữ liệu từ Firebase không phải dict mà là {type(data)}")
        return {}

    # In debug: số lượng sensor groups và một vài key
    keys = list(data.keys())
    print(f"DEBUG: Lấy được {len(keys)} sensor groups: {keys[:5]}{'...' if len(keys) > 5 else ''}")

    # 4. Parse từng node con
    records = []

    for sensor, node_value in data.items():
        node_snippet = repr(node_value)[:100].replace("\n", "\\n")
        print(f"DEBUG: Node '{sensor}' snippet: {node_snippet} …")
        try:
            parsed = parse_node(sensor, node_value, [])
            if not isinstance(parsed, list):
                print(f"⚠️ parse_node trả về không phải list cho sensor '{sensor}'.")
                continue
            if parsed:
                records.extend(parsed)
            else:
                print(f"DEBUG: parse_node cho '{sensor}' trả list rỗng.")
        except Exception as e:
            print(f"🔴 Lỗi khi parse_node cho sensor '{sensor}': {e}")
            continue

    # 5. Nếu không có record nào
    if not records:
        print("ℹ️ Sau khi parse_node, không có records nào.")
        return {}

    # 6. Tạo DataFrame
    try:
        df = pd.DataFrame(records)
    except Exception as e:
        print(f"🔴 Lỗi khi tạo DataFrame từ records: {e}")
        return {}

    # 7. Kiểm tra cột 'sensor' và 'time'
    if 'sensor' not in df.columns or 'time' not in df.columns:
        print(f"🔴 DataFrame thiếu cột 'sensor' hoặc 'time'. Columns hiện tại: {df.columns.tolist()}")
        return {}

    # 8. Sắp xếp
    try:
        df.sort_values(['sensor', 'time'], inplace=True)
    except Exception as e:
        print(f"⚠️ Lỗi khi sort_values: {e} — vẫn tiếp tục group không sort.")

    # 9. Group theo sensor rồi set_index('time')
    grouped = {}
    try:
        for sensor_name, group_df in df.groupby('sensor'):
            try:
                grouped[sensor_name] = group_df.set_index('time')
            except Exception as ee:
                print(f"⚠️ Lỗi khi set_index('time') cho sensor '{sensor_name}': {ee} — Lưu nguyên DataFrame.")
                grouped[sensor_name] = group_df
    except Exception as e:
        print(f"🔴 Lỗi khi nhóm theo 'sensor': {e}")
        return {}

    # 10. In debug: số bản ghi mỗi group
    for s, df_group in grouped.items():
        print(f"DEBUG: Sensor '{s}' có {len(df_group)} bản ghi.")

    return grouped

# -----------------------------------------
# Thêm các hàm liên quan tới user authentication
# -----------------------------------------

def create_user_profile(user_id, ten, tuoi, dia_chi, gioi_tinh):
    """
    Tạo mới hoặc cập nhật hồ sơ người dùng và lưu (plain text) dưới node "UserCreds".
    user_id: string
    Hồ sơ lưu tại: /Users/<user_id>/Profile
    Credentials lưu tại: /UserCreds/<user_id> => password
    """
    # Init Firebase nếu cần
    init_firebase()

    # Lưu credentials
    creds_ref = db.reference(f"/UserCreds/{user_id}")
    try:
        print(f"✅ Đã lưu credential cho user `{user_id}`.")
    except Exception as e:
        print(f"🔴 Lỗi khi lưu credential: {e}")
        raise

    # Lưu profile
    profile_ref = db.reference(f"/Users/{user_id}/Profile")
    data = {
        "Tên": ten,
        "Tuổi": tuoi,
        "Địa chỉ": dia_chi,
        "Giới tính": gioi_tinh
    }
    try:
        profile_ref.set(data)
        print(f"✅ Đã lưu profile cho user `{user_id}`.")
    except Exception as e:
        print(f"🔴 Lỗi khi lưu profile: {e}")
        raise


def get_user_profile(user_id):
    """
    Lấy hồ sơ user từ /Users/<user_id>/Profile. Trả dict hoặc None nếu không tồn tại.
    """
    init_firebase()
    try:
        profile_ref = db.reference(f"/Users/{user_id}/Profile")
        profile = profile_ref.get()
        return profile
    except Exception as e:
        print(f"🔴 Lỗi khi đọc profile: {e}")
        return None

def list_all_users():
    """
    Danh sách tất cả user_id có trong /Users.
    """
    init_firebase()
    try:
        users_ref = db.reference("/Users")
        data = users_ref.get() or {}
        return list(data.keys())
    except Exception as e:
        print(f"🔴 Lỗi khi list_all_users: {e}")
        return []
