import pickle

path = 'skin_label_encoder.pkl'  # Nếu bạn đang ở đúng thư mục chứa file

with open(path, 'rb') as f:
    obj = pickle.load(f)

print("Kiểu dữ liệu:", type(obj))

if hasattr(obj, 'classes_'):  # Trường hợp LabelEncoder
    print("Classes:", list(obj.classes_))
elif isinstance(obj, dict):
    print("Dictionary keys:", list(obj.keys()))
elif isinstance(obj, list):
    print("List items:", obj)
else:
    print("Unknown object:", obj)
