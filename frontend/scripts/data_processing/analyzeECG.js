/**
 * Gửi tín hiệu ECG (mảng giá trị) đến server backend để phân tích
 * @param {number[]} ecgArray - Mảng giá trị ECG
 * @returns {Promise<Object>} - Kết quả JSON từ backend
 */
async function analyzeECG(ecgArray) {
    // Kiểm tra ecgArray là mảng và có ít nhất 1 phần tử số
    if (!Array.isArray(ecgArray) || ecgArray.length === 0 || !ecgArray.every(x => typeof x === 'number')) {
        console.error('❌ Đầu vào ecgArray không hợp lệ:', ecgArray);
        return { error: 'Input ECG array is invalid' };
    }

    try {
        const response = await fetch('https://bio-signal-processing.onrender.com/analyze_ecg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                signal: ecgArray,
                sampling_rate: 400
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (err) {
        console.error('❌ ECG analysis error:', err);
        return { error: 'Failed to analyze ECG', details: err.message };
    }
}

export default analyzeECG;
