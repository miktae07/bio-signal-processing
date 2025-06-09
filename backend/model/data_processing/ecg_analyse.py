from model.data_processing.utils import *
from model.analyse import filter_by_time, compute_window_stats
from tensorflow.keras.models import load_model
from scipy import signal
from pathlib import Path

# Mapping classes
CLASS_MAPPING = {
    0: 'N',  # Non-ecotic beats (normal beat)
    1: 'S',  # Supraventricular ectopic beats
    2: 'V',  # Ventricular ectopic beats
    3: 'F',  # Fusion Beats
    4: 'Q'   # Unknown Beats
}

BASE_DIR = Path(__file__).resolve().parent.parent
print("Current working directory for ECG processing:", BASE_DIR)
WEIGHTS_DIR = BASE_DIR / "weights"

def preprocess_ecg_signal(input_signal, sampling_rate=400, target_length=186):
    """
    Tiền xử lý tín hiệu ECG theo chuẩn MIT-BIH (đã điều chỉnh cho tín hiệu ngắn)
    Args:
        input_signal: numpy array tín hiệu ECG thô (thường 400 samples cho 1 giây)
        sampling_rate: tần số lấy mẫu của tín hiệu đầu vào (Hz)
        target_length: độ dài mục tiêu sau khi xử lý
    Returns:
        processed_beats: list các heartbeat đã được tiền xử lý
    """
    print(f"Processing signal with {len(input_signal)} samples at {sampling_rate}Hz")

    # Chuyển về các số dương bằng cách lấy giá trị tuyệt đối
    print("Input signal (before processing):")
    if len(input_signal) > 20:
        print(f"First 10: {input_signal[:10]}")
        print(f"Last 10: {input_signal[-10:]}")
    else:
        print(input_signal)
    input_signal = np.abs(input_signal)

    print(f"Converted to absolute values. Range: {input_signal.min():.2f} to {input_signal.max():.2f}")
    if len(input_signal) > 20:
        print(f"First 10: {input_signal[:10]}")
        print(f"Last 10: {input_signal[-10:]}")
    else:
        print(input_signal)
    
    # Đối với tín hiệu ngắn (1 giây), xử lý trực tiếp mà không detect R-peaks
    # Normalize về range 0-1 (giống MIT-BIH processing)
    if np.ptp(input_signal) > 0:
        normalized_signal = (input_signal - input_signal.min()) / np.ptp(input_signal)
    else:
        # Nếu tín hiệu flat, giữ nguyên
        normalized_signal = input_signal.copy()

    print("\nAfter normalization (range 0-1):")
    if len(normalized_signal) > 20:
        print(f"First 10: {normalized_signal[:10]}")
        print(f"Last 10: {normalized_signal[-10:]}")
    else:
        print(normalized_signal)
    
    # Resample từ sampling_rate xuống 125Hz (giống MIT-BIH)
    newsize = int((len(normalized_signal) * 125 / sampling_rate) + 0.5)
    resampled_signal = signal.resample(normalized_signal, newsize)
    
    print(f"\nAfter resampling to 125Hz ({len(resampled_signal)} samples):")
    if len(resampled_signal) > 20:
        print(f"First 10: {resampled_signal[:10]}")
        print(f"Last 10: {resampled_signal[-10:]}")
    else:
        print(resampled_signal)
    
    # Điều chỉnh độ dài tín hiệu về target_length (186 samples)
    if len(resampled_signal) > target_length:
        # Nếu tín hiệu dài hơn target_length (186), cắt phần giữa tín hiệu
        # Ví dụ: tín hiệu dài 200 samples, cần cắt về 186 samples
        # start_idx = (200 - 186) // 2 = 7 
        # Lấy từ index 7 đến 7+186 = 193, giữ lại phần giữa quan trọng nhất
        start_idx = (len(resampled_signal) - target_length) // 2
        resampled_signal = resampled_signal[start_idx:start_idx + target_length]
        print(f"\nSignal truncated to {target_length} samples:")
        if len(resampled_signal) > 20:
            print(f"First 10: {resampled_signal[:10]}")
            print(f"Last 10: {resampled_signal[-10:]}")
        else:
            print(resampled_signal)
    else:
        # Nếu tín hiệu ngắn hơn target_length (186), thêm số 0 vào cuối
        # Ví dụ: tín hiệu dài 150 samples, cần thêm 36 số 0 vào cuối
        # zerocount = 186 - 150 = 36
        # Dùng np.pad để thêm số 0 vào cuối tín hiệu
        zerocount = target_length - len(resampled_signal)
        resampled_signal = np.pad(resampled_signal, (0, zerocount), 'constant', constant_values=(0.0, 0.0))
        print(f"\nSignal padded with {zerocount} zeros to reach {target_length} samples:")
        if len(resampled_signal) > 20:
            print(f"First 10: {resampled_signal[:10]}")
            print(f"Last 10: {resampled_signal[-10:]}")
        else:
            print(resampled_signal)

    return [resampled_signal]

def predict_ecg(input_signal, sampling_rate=400):
    """
    Dự đoán kết quả từ tín hiệu ECG đầu vào
    Args:
        input_signal: numpy array tín hiệu ECG thô
        sampling_rate: tần số lấy mẫu của tín hiệu đầu vào (Hz)
    Returns:
        results: list các kết quả dự đoán cho từng heartbeat
    """
    # Load model đã train
    best_ecg_model = 'best_ecg_model.h5'
    model = load_model(WEIGHTS_DIR/best_ecg_model)
  
    # Tiền xử lý tín hiệu ECG
    processed_beats = preprocess_ecg_signal(input_signal, sampling_rate)
    
    results = []
    for i, beat in enumerate(processed_beats):
        # Reshape cho model
        input_data = beat.reshape(1, 186, 1)
        
        # Dự đoán
        predictions = model.predict(input_data, verbose=0)
        
        # Lấy kết quả dự đoán
        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        class_name = CLASS_MAPPING[predicted_class]
        
        results.append({
            'beat_index': i + 1,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'class_name': class_name,
            'probabilities': predictions[0]
        })
    
    return results

def predict_single_beat(input_signal, sampling_rate=400):
    """
    Dự đoán cho một heartbeat đơn lẻ (tương thích với code cũ)
    Args:
        input_signal: numpy array tín hiệu ECG
        sampling_rate: tần số lấy mẫu
    Returns:
        predicted_class, confidence, class_name
    """
    results = predict_ecg(input_signal, sampling_rate)
    if results:
        # Trả về kết quả của beat đầu tiên
        result = results[0]
        return result['predicted_class'], result['confidence'], result['class_name']
    else:
        return None, 0.0, "No heartbeat detected"

# Example usage:
if __name__ == "__main__":
    # input_signal = np.array([-1530, -1586, -1621, -1542, -1498, -1830, -1724, -1511, -1461, -1826, -1810, -1547, -1451, -1656, -1601, -1511, -1496, -1544, -1496, -1505, -1521, -1623, -1603, -1520, -1496, -1496, -1492, -1512, -1527, -1845, -1766, -1526, -1455, -1559, -1496, -1496, -1517, -2014, -1947, -1555, -1420, -2256, -2125, -1562, -1372, -2204, -2127, -1576, -1371, -2140, -2062, -1566, -1388, -2162, -2080, -1562, -1380, -2123, -2028, -1564, -1397, -2215, -2094, -1560, -1380, -2152, -2049, -1551, -1385, -2017, -1948, -1551, -1415, -1766, -1739, -1534, -1466, -1259, -1213, -1475, -1588, -1586, -1601, -1534, -1509, -1434, -1455, -1513, -1539, -1410, -1432, -1511, -1546, -1922, -1798, -1510, -1443, -1665, -1600, -1517, -1500, -1533, -1538, -1527, -1523, -1189, -1185, -1478, -1593, -1724, -1643, -1513, -1482, -1549, -1532, -1516, -1517, -1285, -1380, -1530, -1565, -1818, -1667, -1494, -1474, -1328, -1290, -1481, -1572, -1482, -1381, -1476, -1546, -1839, -1662, -1485, -1470, -1285, -1336, -1513, -1574, -1572, -1520, -1509, -1521, -1662, -1586, -1508, -1499, -1492, -1404, -1480, -1538, -1405, -1405, -1506, -1545, -1404, -1439, -1516, -1546, -1408, -1416, -1513, -1549, -1496, -1481, -1511, -1534, -1594, -1569, -1517, -1509, -1291, -1334, -1508, -1567, -1480, -1354, -1463, -1550, -1613, -1614, -1534, -1507, -1469, -1457, -1509, -1534, -1534, -1497, -1509, -1521, -1282, -1304, -1496, -1569, -1205, -1284, -1509, -1586, -1376, -1356, -1498, -1560, -1219, -1202, -1477, -1590, -1393, -1405, -1509, -1548, -1137, -1191, -1492, -1601, -1414, -1393, -1496, -1548, -993, -1091, -1496, -1633, -1091, -1078, -1470, -1624, -1182, -1142, -1465, -1604, -956, -1001, -1471, -1646, -1326, -1276, -1479, -1571, -865, -971, -1484, -1663, -742, -855, -1471, -1698, -1289, -1332, -1504, -1578, -51, -683, -1601, -1797, -1148, -1252, -1509, -1606, -1237, -1349, -1533, -1586, -1045, -1302, -1563, -1617, -1163, -1302, -1525, -1595, -565, -993, -1575, -1702, -668, -994, -1546, -1701, -1223, -1326, -1530, -1599, -934, -1185, -1550, -1663, -1287, -1372, -1523, -1575, -864, -1164, -1560, -1646, -515, -941, -1567, -1733, -1013, -1185, -1529, -1639, -844, -1127, -1559, -1663, -269, -875, -1612, -1759, -694, -1027, -1553, -1715, -1144, -1314, -1537, -1624, -559, -1026, -1594, -1711, -347, -888, -1596, -1749, -268, -851, -1604, -1759, -229, -790, -1591, -1798, 0, -635, -1612, -1857, -663, -978, -1543, -1735, -348, -856, -1585, -1759, -650, -1047, -1575, -1691, -89, -753, -1617, -1810, -359, -886, -1592, -1748, -247, -824, -1601, -1787, -127, -774, -1617, -1838, -486, -921, -1573, -1770, -326, -892, -1603, -1758, 0, -606, -1614, -1826, -33, -773, -1640, -1837, -127, -733, -1606, -1854, -529, -963, -1581, -1741, -185, -803, -1608, -1776, 0, -663, -1639])
    input_signal = np.array([-1498, -1470, -1521, -1534, -1550, -1712, -1720, -1546, -1500, -1693, -1661, -1525, -1509, -1935, -1822, -1523, -1464, -1866, -1765, -1513, -1477, -1969, -1838, -1517, -1455, -1687, -1674, -1536, -1509, -1891, -1787, -1520, -1467, -1591, -1577, -1523, -1527, -1707, -1659, -1521, -1507, -1478, -1532, -1537, -1546, -1702, -1646, -1521, -1509, -1732, -1677, -1522, -1504, -1947, -1791, -1506, -1461, -1589, -1624, -1543, -1522, -1334, -1413, -1530, -1575, -1302, -1403, -1537, -1581, -1456, -1483, -1532, -1560, -1355, -1448, -1546, -1575, -1367, -1417, -1529, -1575, -1474, -1481, -1525, -1586, -1085, -1303, -1567, -1644, -1625, -1552, -1513, -1553, -1986, -1792, -1503, -1485, -1827, -1675, -1501, -1539, -1411, -1472, -1538, -1615, -1453, -1494, -1542, -1618, -1592, -1562, -1534, -1552, -1658, -1590, -1521, -1542, -1534, -1536, -1537, -1562, -1970, -1733, -1491, -1448, -1484, -1567, -1565, -1588, -1582, -1548, -1534, -1623, -1593, -1534, -1523, -1584, -1841, -1650, -1501, -1548, -1532, -1534, -1536, -1662, -1492, -1482, -1534, -1560, -1613, -1564, -1534, -1530, -1588, -1560, -1535, -1479, -1427, -1508, -1561, -1638, -2059, -1700, -1459, -1362, -1068, -1380, -1620, -1662, -1600, -1509, -1524, -1591, -1996, -1677, -1472, -1456, -1496, -1501, -1547, -1508, -1496, -1490, -1546, -1607, -1741, -1552, -1497, -1590, -1896, -1614, -1487, -1285, -1612, -1546, -1540, -1508, -1614, -1523, -1530, -1565, -1750, -1560, -1509, -1278, -1237, -1444, -1603, -1505, -1559, -1506, -1542, -1598, -1397, -1469, -1533, -1639, -1456, -1478, -1522, -1633, -1483, -1485, -1522, -1581, -1405, -1475, -1534, -1638, -1535, -1509, -1519, -1559, -1472, -1509, -1530, -1527, -1363, -1474, -1546, -1617, -1479, -1494, -1522, -1627, -1530, -1509, -1509, -1551, -1434, -1496, -1537, -1549, -1427, -1493, -1536, -1596, -1459, -1488, -1523, -1486, -1385, -1491, -1546, -1460, -1354, -1484, -1550, -1625, -1498, -1501, -1521, -1618, -1509, -1505, -1517, -1343, -1237, -1483, -1578, -1347, -1237, -1476, -1575, -1600, -1468, -1494, -1533, -1635, -1536, -1509, -1519, -1592, -1575, -1533, -1513, -1650, -1602, -1525, -1509, -1613, -1612, -1542, -1509, -1490, -1471, -1519, -1534, -1509, -1483, -1521, -1534, -1658, -1576, -1514, -1509, -1650, -1578, -1517, -1505, -1691, -1623, -1526, -1496, -1379, -1377, -1511, -1560, -1688, -1595, -1517, -1504, -1495, -1458, -1517, -1536, -1509, -1465, -1509, -1534, -1702, -1612, -1513, -1496, -1574, -1549, -1524, -1519, -1535, -1509, -1522, -1530, -1565, -1545, -1533, -1521, -1613, -1579, -1529, -1506, -1484, -1514, -1534, -1530, -1638, -1556, -1509, -1511, -1543, -1510, -1521, -1527, -1461, -1457, -1519, -1537, -1534, -1515, -1521, -1524, -1722, -1628, -1516, -1488, -1444, -1473, -1530, -1535, -1638, -1558, -1510, -1509, -1571, -1517, -1516, -1522, -1692, -1584, -1509, -1501])
    
    # Dự đoán cho tất cả heartbeats trong tín hiệu ECG
    print("=== Dự đoán cho tất cả heartbeats ===")
    # Gọi hàm predict_ecg với tín hiệu đầu vào và tần số lấy mẫu 400Hz
    # Hàm sẽ trả về danh sách các kết quả dự đoán cho từng heartbeat
    results = predict_ecg(input_signal, sampling_rate=400)
    
    for result in results:
        print(f"Beat {result['beat_index']}:")
        print(f"  Predicted class: {result['predicted_class']} ({result['class_name']})")
        print(f"  Confidence: {result['confidence']:.3f}")
        print(f"  All probabilities: {result['probabilities']}")
        print()

    print("=== Dự đoán cho beat đầu tiên ===")
    predicted_class, confidence, class_name = predict_single_beat(input_signal)
    print(f"Predicted class number: {predicted_class}")
    print(f"Predicted class name: {class_name}")
    print(f"Confidence: {confidence:.2f}")

def analyze_ecg_window(
    df_ECG,                     # pandas.DataFrame chứa ít nhất hai cột ['timestamp', 'value']
    start: datetime,            # thời điểm bắt đầu (datetime)
    end: datetime               # thời điểm kết thúc (datetime)
) -> Tuple[Dict[str, float], str]:
    # Debug: In thông tin đầu vào
    print("=== Debugging analyze_ecg_window ===")
    print(f"Input df_ECG type: {type(df_ECG)}")
    print(f"df_ECG shape: {df_ECG.shape}")
    print(f"df_ECG columns: {df_ECG.columns.tolist()}")
    print(f"Start time: {start}")
    print(f"End time: {end}")

    window_series = filter_by_time(df_ECG, start, end)['value']
    print(f"Window series length: {len(window_series)} samples")
    
    if window_series.empty:
        return ({'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0}, 'No Data')
    stats = compute_window_stats(window_series)
    
    ecg_array = window_series.to_numpy(dtype=float)
    print(f"ECG array shape: {ecg_array.shape}")
    
    _, confidence, class_name = predict_single_beat(ecg_array, sampling_rate=400)
    print(f"Predicted class: {class_name}")
    print (f"Confidence: {confidence}")
    class_name = map_lang(class_name)

    return stats, class_name, confidence

