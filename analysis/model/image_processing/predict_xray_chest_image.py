import torch
from torchvision import transforms
from torchvision.models import densenet121
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Union

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"

# Danh sách 14 bệnh của ChestX-ray14
CHEST_XRAY_CLASSES = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural_Thickening", "Hernia"
]

def get_preprocessing_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

def load_chexnet_model(weights_path: str, device: torch.device) -> torch.nn.Module:
    model = densenet121(pretrained=False)
    model.classifier = torch.nn.Linear(1024, 14)

    checkpoint = torch.load(weights_path, map_location=device)
    state_dict = checkpoint.get('state_dict', checkpoint)

    # Load với strict=False để ignore những keys không khớp
    model.load_state_dict(state_dict, strict=False)

    model.to(device)
    model.eval()
    return model

def predict_chexnet(
    model: torch.nn.Module,
    image_input: Union[str, Image.Image],
    device: torch.device
) -> Image.Image:
    """
    Nhận đường dẫn ảnh (str) hoặc PIL.Image, trả về ảnh RGB có chú thích kết quả.
    """
    # 1) Chuẩn bị ảnh dưới dạng PIL.Image
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise ValueError("predict_chexnet chỉ nhận str (đường dẫn) hoặc PIL.Image.Image")

    # 2) Tiền xử lý cho model
    preprocess = get_preprocessing_transform()
    input_tensor = preprocess(img).unsqueeze(0).to(device)

    # 3) Inference
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.sigmoid(output)[0].cpu().tolist()

    # 4) Vẽ chú thích lên ảnh (resize cho gọn nếu cần)
    result_img = img.resize((224, 224))
    draw = ImageDraw.Draw(result_img)
    try:
        font = ImageFont.truetype("arial.ttf", size=12)
    except:
        font = ImageFont.load_default()

    y = 5
    for disease, prob in zip(CHEST_XRAY_CLASSES, probs):
        if prob > 0.5:
            text = f"{disease}: {prob:.2f}"
            draw.text((5, y), text, fill="red", font=font)
            y += 15

    return result_img