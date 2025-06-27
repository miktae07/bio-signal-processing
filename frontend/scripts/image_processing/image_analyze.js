import { getBackendAddress } from '../backend_config.js';

/**
 * Gửi hình ảnh đến server backend để phân tích (dự đoán đối tượng hoặc phân đoạn)
 * @param {File} imageFile - File hình ảnh đầu vào (từ input type="file")
 * @param {string} imageType - Loại hình ảnh (X-Ray, MRI, Ultrasound, CT)
 * @param {string} bodyPart - Bộ phận cơ thể (Chest, Brain, Liver, Abdomen)
 * @returns {Promise<Object>} - Kết quả JSON từ backend
 */

const SUPPORTED_TYPES = ["X-Ray", "MRI", "Ultrasound", "CT", "Photo"];
const SUPPORTED_BODY_PARTS = ["Chest", "Brain", "Liver", "Abdomen", "Skin"];

async function analyzeImage(imageFile, imageType, bodyPart) {
    // Kiểm tra đầu vào
    if (!(imageFile instanceof File)) {
        console.error('❌ Đầu vào imageFile không hợp lệ:', imageFile);
        return { error: 'Input image file is invalid' };
    }
    if (!SUPPORTED_TYPES.includes(imageType)) {
        console.error('❌ Loại hình ảnh không hợp lệ:', imageType);
        return { error: 'Invalid image type. Must be X-Ray, MRI, Ultrasound, or CT' };
    }
    if (!SUPPORTED_BODY_PARTS.includes(bodyPart)) {
        console.error('❌ Bộ phận cơ thể không hợp lệ:', bodyPart);
        return { error: 'Invalid body part. Must be Chest, Brain, Liver, or Abdomen' };
    }

    try {
        const backendURL = getBackendAddress(); // lấy địa chỉ backend hiện tại

        // Tạo FormData để gửi file và metadata
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('image_type', imageType);
        formData.append('body_part', bodyPart);

        // Gửi yêu cầu POST đến backend
        console.info('Get image result from URL:', `${backendURL}/predict_image`);
        const response = await fetch(`${backendURL}/predict_image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (err) {
        console.error('❌ Image analysis error:', err);
        return { error: 'Failed to analyze image', details: err.message };
    }
}

export default analyzeImage;
