const userProfiles = {
    user1: { Tên: "Nguyễn Văn A", Tuổi: "30", "Địa chỉ": "123 Đường ABC, Quận XYZ, Thành phố ABC", "Giới tính": "Nam" },
    user2: { Tên: "Trần Thị B", Tuổi: "25", "Địa chỉ": "456 Đường DEF, Quận UVW, Thành phố ABC", "Giới tính": "Nữ" },
    user3: { Tên: "Lê Văn C", Tuổi: "40", "Địa chỉ": "789 Đường GHI, Quận RST, Thành phố ABC", "Giới tính": "Nam" }
};

export function updateUserProfile(userId) {
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

export function setGreeting() {
    const now = moment().utcOffset('+07:00'); // Đặt múi giờ UTC+7
    console.log("Now ", now.format());
    const hour = now.hour();
    const greeting = hour < 12 ? "Chào buổi sáng" : hour < 18 ? "Chào buổi chiều" : "Chào buổi tối";
    document.getElementById('greeting').textContent = greeting;
}

export function mapLang(text) {
    const mapping = {
        "Bradycardia": "Nhịp tim chậm (Bradycardia)",
        "Normal BPM": "Nhịp tim bình thường",
        "Normal Temperature": "Nhiệt độ bình thường",
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
        "Temp": "Nhiệt độ cơ thể",
          // Nhóm bệnh da liễu từ label_encoder
    "Acne and Rosacea Photos": "Mụn trứng cá và bệnh đỏ da (Rosacea)",
    "Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions": "Dày sừng ánh sáng, ung thư biểu mô tế bào đáy và tổn thương ác tính khác",
    "Atopic Dermatitis Photos": "Viêm da cơ địa",
    "Cellulitis Impetigo and other Bacterial Infections": "Viêm mô tế bào, chốc lở và nhiễm khuẩn da khác",
    "Eczema Photos": "Chàm (eczema)",
    "Exanthems and Drug Eruptions": "Phát ban và phản ứng thuốc trên da",
    "Herpes HPV and other STDs Photos": "Herpes, HPV và các bệnh lây qua đường tình dục khác",
    "Light Diseases and Disorders of Pigmentation": "Rối loạn sắc tố và các bệnh da do ánh sáng",
    "Lupus and other Connective Tissue diseases": "Lupus và bệnh mô liên kết khác",
    "Melanoma Skin Cancer Nevi and Moles": "U hắc tố, ung thư da, nốt ruồi và bớt",
    "Poison Ivy Photos and other Contact Dermatitis": "Viêm da tiếp xúc do cây độc và các nguyên nhân khác",
    "Psoriasis pictures Lichen Planus and related diseases": "Vảy nến, lichen phẳng và bệnh liên quan",
    "Seborrheic Keratoses and other Benign Tumors": "Dày sừng tiết bã và u lành tính khác",
    "Systemic Disease": "Bệnh hệ thống",
    "Tinea Ringworm Candidiasis and other Fungal Infections": "Nấm da, hắc lào, nấm Candida và các nhiễm nấm khác",
    "Urticaria Hives": "Mề đay",
    "Vascular Tumors": "U mạch máu",
    "Vasculitis Photos": "Viêm mạch",
    "Warts Molluscum and other Viral Infections": "Mụn cóc, u mềm lây và các nhiễm virus khác",
    };
    return mapping[text] || text;
}

export function getUnit(sensor) {
    sensor = sensor.toUpperCase();
    if (sensor === "BPM") return "bpm";
    if (sensor === "SPO2") return "%";
    if (sensor === "ECG" || sensor === "EEG") return "µV";
    if (sensor === "TEMP") return "°C";
    return "";
}

export function getSensorIcon(sensor) {
    sensor = sensor.toUpperCase();
    if (sensor.includes("BPM") || sensor.includes("HEART")) return "❤️";
    if (sensor.includes("SPO2") || sensor.includes("OXY")) return "🫁";
    if (sensor.includes("ECG")) return "🫀";
    if (sensor.includes("TEMP") || sensor.includes("NHIỆT")) return "🌡️";
    return "🔧";
}

