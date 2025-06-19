import pandas as pd

# Mapping từ số sang tên lớp
LABEL_MAP = {
    '0': 'N',  # Normal
    '1': 'S',  # Supraventricular
    '2': 'V',  # Ventricular
    '3': 'F',  # Fusion
    '4': 'Q'   # Unknown
}

def analyze_labels(csv_file):
    try:
        # Đọc dữ liệu
        df = pd.read_csv(csv_file, header=None)
        labels = df.iloc[:, -1]

        # Gom các chỉ số dòng theo từng lớp
        class_indices = {}
        for idx, label in labels.items():
            label_str = str(int(float(label)))  # '0.0' -> '0'
            class_name = LABEL_MAP.get(label_str, 'Unknown')
            class_indices.setdefault(class_name, []).append(idx)

        # In kết quả
        print("\nRow indices by class label:")
        for class_name, indices in class_indices.items():
            print(f"  - Class {class_name} ({len(indices)} beats): {indices}")

    except Exception as e:
        print(f"❌ Error processing CSV: {e}")

# Chạy khi gọi trực tiếp file
if __name__ == "__main__":
    csv_file = "model/sample/mitbih_test.csv"  # Cập nhật đường dẫn nếu cần
    analyze_labels(csv_file)
