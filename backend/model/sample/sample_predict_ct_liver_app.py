from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import os
from pathlib import Path


def predict_mask(image_path, model_path, target_size=(128, 128), threshold=0.5):
    # Load image and convert to RGB
    img = Image.open(image_path).convert('RGB')
    img_resized = img.resize(target_size)

    # Preprocess
    arr = np.array(img_resized).astype(np.float32) / 255.0
    batch = np.expand_dims(arr, 0)  # Add batch dimension

    # Load model
    model = load_model(model_path, compile=False)

    # Predict
    pred = model.predict(batch)[0]
    mask = (pred > threshold).astype(np.uint8) * 255
    if mask.ndim == 3:
        mask = mask[..., 0]

    return img_resized, Image.fromarray(mask)


if __name__ == '__main__':
    # Define root directory
    root_dir = Path(__file__).resolve().parent.parent
    print(f"Debug: Root directory is {root_dir}")

    # Define weights directory and model path
    weights_dir = root_dir / 'weights'
    model_path = weights_dir / 'best_unet_resnet18_model.keras'

    # Debug: Print model path
    print(f"Debug: Model path is {model_path}")
    print(f"Debug: Model path exists: {model_path.exists()}")

    # Define image directory and test image path
    image_dir = root_dir  / 'sample'/ 'ct_liver'
    image_path = image_dir / 'test_ct_liver.png'

    # Debug: Print image path
    print(f"Debug: Image path is {image_path}")
    print(f"Debug: Image path exists: {image_path.exists()}")

    # Predict mask
    input_img, pred_mask = predict_mask(image_path, model_path)

    # Save predicted mask
    output_mask_path = image_dir / 'pred_mask.png'
    pred_mask.save(output_mask_path)
    print(f"✅ Saved predicted mask to: {output_mask_path}")

    # Save comparison figure
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(input_img, cmap='gray')
    axs[0].set_title('Input Image')
    axs[0].axis('off')

    axs[1].imshow(pred_mask, cmap='gray')
    axs[1].set_title('Predicted Mask')
    axs[1].axis('off')

    plt.tight_layout()
    fig_path = image_dir / 'pred_result.png'
    plt.savefig(fig_path)
    print(f"✅ Saved comparison figure to: {fig_path}")