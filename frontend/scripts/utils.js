const userProfiles = {
    user1: { Tên: "Nguyễn Văn A", Tuổi: "30", "Địa chỉ": "123 Đường ABC, Quận XYZ, Thành phố ABC", "Giới tính": "Nam" },
    user2: { Tên: "Trần Thị B", Tuổi: "25", "Địa chỉ": "456 Đường DEF, Quận UVW, Thành phố ABC", "Giới tính": "Nữ" },
    user3: { Tên: "Lê Văn C", Tuổi: "40", "Địa chỉ": "789 Đường GHI, Quận RST, Thành phố ABC", "Giới tính": "Nam" }
};

function updateUserProfile(userId) {
    const profile = userProfiles[userId] || {
        Tên: "Nguyễn Văn A",
        Tuổi: "30",
        "Địa chỉ": "123 Đường ABC, Quận XYZ, Thành phố ABC",
        "Giới tính": "Nam"
    };
    document.getElementById('userName').textContent = profile.Tên;
    document.getElementById('userAge').textContent = profile.Tuổi;
    document.getElementById('userAddress').textContent = profile["Địa chỉ"];
    document.getElementById('userGender').textContent = profile["Giới tính"];
}

function setGreeting() {
    const now = moment().utcOffset('+07:00'); // Đặt múi giờ UTC+7
    console.log("Now ", now.format());
    const hour = now.hour();
    const greeting = hour < 12 ? "Chào buổi sáng" : hour < 18 ? "Chào buổi chiều" : "Chào buổi tối";
    document.getElementById('greeting').textContent = greeting;
}

function mapLang(text) {
    const mapping = {
        "Bradycardia": "Nhịp tim chậm (Bradycardia)",
        "Normal": "Nhịp tim bình thường",
        "Tachycardia": "Nhịp tim nhanh (Tachycardia)",
        "Severe respiratory failure": "Suy hô hấp nặng (SpO2 < 90%)",
        "Mild respiratory failure": "Suy hô hấp nhẹ (90% ≤ SpO2 < 95%)",
        "Normal SpO2": "SpO2 bình thường (≥ 95%)",
        "Hypothermia": "Hạ thân nhiệt",
        "Fever": "Sốt",
        "Abnormal": "Bất thường",
        "Unknown": "Không xác định",
        "Nhịp tim chậm (Bradycardia)": "Bradycardia (Slow heart rate)",
        "Nhịp tim bình thường": "Normal heart rate",
        "Nhịp tim nhanh (Tachycardia)": "Tachycardia (Fast heart rate)",
        "Không có dữ liệu BPM": "No BPM data",
        "Suy hô hấp nặng (SpO2 < 90%)": "Severe respiratory failure (SpO2 < 90%)",
        "Suy hô hấp nhẹ (90% ≤ SpO2 < 95%)": "Mild respiratory failure (90% ≤ SpO2 < 95%)",
        "SpO2 bình thường (≥ 95%)": "Normal SpO2 (≥ 95%)",
        "Không có dữ liệu SpO2": "No SpO2 data",
        "N": "Nhịp tim normal(N)",
        "S": "Nhịp trên thất ngoại tâm thu(S)",
        "V": "Nhịp thất ngoại tâm thu(V)",
        "F": "Nhịp hợp tử(F)",
        "Q": "Nhịp không xác định(Q)",
        "BPM": "Nhịp tim(BPM)",
        "ECG": "Điện tim(ECG)",
        "SpO2": "Nồng độ Oxy trong máu(SpO2)",
        "Temp": "Nhiệt độ cơ thể"
    };
    return mapping[text] || text;
}

function getUnit(sensor) {
    sensor = sensor.toUpperCase();
    if (sensor === "BPM") return "bpm";
    if (sensor === "SPO2") return "%";
    if (sensor === "ECG" || sensor === "EEG") return "µV";
    if (sensor === "TEMP") return "°C";
    return "";
}

function getSensorIcon(sensor) {
    sensor = sensor.toUpperCase();
    if (sensor.includes("BPM") || sensor.includes("HEART")) return "❤️";
    if (sensor.includes("SPO2") || sensor.includes("OXY")) return "🫁";
    if (sensor.includes("ECG")) return "🫀";
    if (sensor.includes("TEMP") || sensor.includes("NHIỆT")) return "🌡️";
    return "🔧";
}