import json

with open("esp32-9c871-firebase-adminsdk-fbsvc-c1266e7f1e.json", "r") as f:
    raw = f.read()
    escaped = json.dumps(raw)

print(escaped)  # copy nội dung in ra để dán vào secrets.toml
