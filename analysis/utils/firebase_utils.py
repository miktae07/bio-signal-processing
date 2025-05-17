# firebase_utils.py
import json
import re
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

def init_firebase():
    if not firebase_admin._apps:
        firebase_json = st.secrets["FIREBASE_CREDENTIALS"]
        cred = credentials.Certificate(json.loads(firebase_json))
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://esp32-9c871-default-rtdb.firebaseio.com/'
        })

def parse_node(sensor, node, path_keys):
    records = []
    if isinstance(node, dict):
        for k, v in node.items():
            records.extend(parse_node(sensor, v, path_keys + [k]))
    else:
        if len(path_keys) >= 6:
            try:
                ts = f"{path_keys[0]}-{path_keys[1].zfill(2)}-{path_keys[2].zfill(2)} " \
                     f"{path_keys[3].zfill(2)}:{path_keys[4].zfill(2)}:{path_keys[5].zfill(2)}"
                base_time = pd.to_datetime(ts)
            except:
                return []
            if sensor == 'ECG':
                vals = [int(v) for v in re.findall(r'-?\d+', str(node))]
                for i, v in enumerate(vals):
                    records.append({'sensor': sensor,
                                    'time': base_time + pd.to_timedelta(i * 4, unit='ms'),
                                    'value': v})
            else:
                try:
                    val = float(node)
                except:
                    val = node
                records.append({'sensor': sensor, 'time': base_time, 'value': val})
    return records

def get_sensor_groups():
    init_firebase()
    data_ref = db.reference('/')
    data = data_ref.get() or {}

    records = []
    for sensor, d in data.items():
        records.extend(parse_node(sensor, d, []))
    if not records:
        return {}

    df = pd.DataFrame(records)
    df.sort_values(['sensor', 'time'], inplace=True)
    return {s: g.set_index('time') for s, g in df.groupby('sensor')}
