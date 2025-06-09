function analyzeBPM(value) {
    let result = 'Normal';
    if (value < 60) {
        result = 'Bradycardia';
    } else if (value > 100) {
        result = 'Tachycardia';
    }
    return result;
}

export default analyzeBPM;