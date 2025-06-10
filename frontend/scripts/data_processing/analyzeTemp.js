function analyzeTemp(value) {
    let result = 'Normal Temperature';
    if (value < 36) {
        result = 'Hypothermia';
    } else if (value > 38) {
        result = 'Fever';
    }
    return result;
}

export default analyzeTemp;