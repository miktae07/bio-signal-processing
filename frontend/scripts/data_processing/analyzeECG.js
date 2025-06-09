function analyzeECG(value) {
    let result = 'Normal';
    if (value > 100) {
        result = 'Abnormal';
    }
    return result;
}

export default analyzeECG;