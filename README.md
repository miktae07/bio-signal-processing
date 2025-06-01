# Bio-Signal-Processing

**Authors:** Nguyễn Văn Thành, Nguyễn Trí Trọng, Trần Thị Hằng, HaUI

---

## 📘 Giới thiệu

Bio‑Signal‑Processing là dự án hệ thống giám sát sức khỏe đa kênh, thu thập và phân tích dữ liệu sinh học (ECG, nhịp tim, SpO₂, nhiệt độ cơ thể…) theo thời điểmthực. Hệ thống gồm:

* **Firmware (ESP32):** Đọc tín hiệu từ nhiều cảm biến, kết nối Wi-Fi, đẩy dữ liệu lên Firebase Realtime Database.
* **Backend & Dashboard:** Ứng dụng Python/Streamlit để trực quan hóa, phân tích, cảnh báo và xuất báo cáo.
* **Docs:** Hướng dẫn triển khai, sơ đồ kiến trúc, API và các ví dụ mẫu.

Mục tiêu chính là hỗ trợ giám sát liên tục, cảnh báo sớm và xuất báo cáo phân tích chi tiết.

---

## 🚀 Tính năng chính

1. **Thu thập dữ liệu đa kênh:** ECG, SpO₂, nhịp tim, nhiệt độ, v.v.
2. **Trực quan thời điểmthực:** Biểu đồ động, tự động refresh sau mỗi 10 giây.
3. **Phân tích nhanh:** Tính mean, std, min, max cho n mẫu cuối.
4. **Cảnh báo bất thường:** So sánh với threshold (mean ± 2·std).
5. **Xuất báo cáo:** PDF/TXT, tải về chỉ với một nút.
6. **Đa trang:** Chuyển giữa Dashboard và Analysis bằng sidebar hoặc nút.

---

## 📂 Cấu trúc thư mục

```bash
bio-signal-processing/
├── analysis/          # Ứng dụng Streamlit: code phân tích và dashboard
│   ├── demo.py        # File chính hiển thị Dashboard và Analysis
│   └── analysis.py    # Trang phân tích tách biệt (multipage)
├── firmware/          # Code nhúng ESP32 (PlatformIO hoặc ESP-IDF)
│   ├── src/
│   └── platformio.ini
├── docs/              # Tài liệu triển khai, sơ đồ, API reference
├── data/              # Dữ liệu mẫu (nếu có) để test offline
├── useful/            # Script hỗ trợ: migrate, clean, export
├── venv/              # Virtual environment Python (không commit lên Git)
├── .gitignore
├── LICENSE
└── README.md          # Tệp này
```

---

## 💻 Cài đặt & Môi trường

### 1. Cài Git

* **Windows:** Tải và cài [Git for Windows](https://gitforwindows.org/) trên giao diện cài đặt chuẩn.
* **macOS:**

  ```bash
  brew install git
  ```
* **Ubuntu/Debian:**

  ```bash
  sudo apt update
  sudo apt install git
  ```

### 2. (Tuỳ chọn) Cài GitHub CLI

* **macOS:** `brew install gh`
* **Ubuntu:** `sudo apt install gh`
* Đăng nhập: `gh auth login`

### 3. Clone repository

```bash
# SSH
git clone git@github.com:miktae07/bio-signal-processing.git
# Hoặc HTTPS
git clone https://github.com/miktae07/bio-signal-processing.git
```

### 4. Thiết lập Python Env

```bash
cd bio-signal-processing
python3 -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Cấu hình Firebase

* Tạo project trên Firebase console, bật Realtime Database.
* Lấy file JSON credentials, lưu vào `secrets.toml` hoặc config Streamlit:

  ```toml
  [secrets]
  FIREBASE_CREDENTIALS = '''<nội dung JSON>'''
  ```

---

## 🛠️ Clone & Push Code

### 1. Tạo nhánh làm việc (feature branch)

```bash
git checkout -b feature/<tên-tính-năng>
```

### 2. Thực hiện thay đổi & Commit

* **Format commit message:**

  ```text
  <type>(<scope>): <mô tả ngắn>

  <thông tin thêm nếu cần>
  ```

  Trong đó `type` có thể là `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

* Ví dụ:

  ```bash
  Modify analysis/demo.py, add function to export PDF
  ```

git add analysis/demo.py
git commit -m "feat(analysis): thêm nút xuất PDF"

````

### 3. Đẩy branch lên remote
```bash
git push -u origin feature/<tên-tính-năng>
````

* Tùy chọn `-u` giúp thiết lập upstream, từ lần sau chỉ cần `git push` hoặc `git pull`.

### 4. Tạo Pull Request và Merge vào `main`

* Trên GitHub, open Pull Request từ `feature/<tên-tính-năng>` về `main`.
* Sau khi review & merge, local bạn cần cập nhật nhánh `main`:

```bash
  git checkout main
  git pull origin main
```

### 5. Đẩy thay đổi trực tiếp lên `main`
Dành cho các cập nhật nhỏ hoặc hotfix, bạn có thể làm trên `main` như sau:
```bash
# Chuyển về main và cập nhật
git checkout main
git pull origin main or git pull --rebase
# Thực hiện thay đổi nhỏ
# git add ... && git commit -m "fix(main): <mô tả>"
# Đẩy trực tiếp lên main
git push origin main
````

---

## ▶️ Chạy ứng dụng

```bash
# Trong thư mục gốc và kích hoạt venv
streamlit run main.py
```

* Mặc định mở Dashboard; dùng sidebar hoặc nút để chuyển sang trang Analysis.

---

## 📝 Hướng dẫn sử dụng

1. **Dashboard:**

   * Chọn sensor cần xem.
   * Biểu đồ , dữ liệu thô, trạng thái (🟢/🔴).
2. **Phân tích:**

   * Nhập số bản ghi cuối `n`, click **Chạy phân tích**.
   * Xem thống kê và biểu đồ nhỏ.
   * Click **Xuất báo cáo** để download PDF/TXT.
3. **Chuyển trang:**

   * Sử dụng sidebar “Chọn trang” hoặc nút **Phân tích** và **Quay về Dashboard**.

---

## 🤝 Đóng góp

1. Fork repo này
2. Tạo nhánh `feature/<tên>`
3. Thực hiện commit với format chuẩn
4. Push và tạo Pull Request

---

## 📃 License

Dự án theo **MIT License**. Xem file [LICENSE](./LICENSE) để biết chi tiết.

---

*Last updated: May 2025*
