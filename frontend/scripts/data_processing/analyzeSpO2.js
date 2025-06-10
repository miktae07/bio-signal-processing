function analyzeSpO2(value) {
    let result = 'Normal SpO2';
    if (value < 90) {
        result = 'Severe respiratory failure';
    } else if (value < 95) {
        result = 'Mild respiratory failure';
    }
    return result;
}

export default analyzeSpO2;