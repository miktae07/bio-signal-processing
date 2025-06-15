import analyzeBPM from './data_processing/analyzeBPM.js';
import analyzeSpO2 from './data_processing/analyzeSpO2.js';
import analyzeTemp from './data_processing/analyzeTemp.js';
import analyzeECG from './data_processing/analyzeECG.js';
import { setGreeting, updateUserProfile, getUnit, getSensorIcon, mapLang } from './utils.js';

// Global debug flag
let isDebugEnabled = false;

// Function to enable debug mode
window.allowDebug = function() {
    isDebugEnabled = true;
    console.log('Debug mode enabled');
};

// Store selected sensors (default: all sensors enabled)
let selectedSensors = JSON.parse(localStorage.getItem('selectedSensors')) || {};

// Function to save selected sensors
function saveSelectedSensors() {
    const checkboxes = document.querySelectorAll('#sensorCheckboxes input[type="checkbox"]');
    const newSelectedSensors = {};
    checkboxes.forEach(checkbox => {
        newSelectedSensors[checkbox.value] = checkbox.checked;
    });
    selectedSensors = newSelectedSensors;
    localStorage.setItem('selectedSensors', JSON.stringify(selectedSensors));
    // Re-render metrics and charts with updated selections
    window.dispatchEvent(new CustomEvent('updateSensorDisplay'));
}

export async function renderMetrics(sensorGroups) {
    if (isDebugEnabled) {
        console.log('[renderMetrics]', sensorGroups);
    }
    const metricsDiv = document.getElementById('metrics');
    if(!metricsDiv) {
        console.error('Element with ID "metrics" not found.');
        return;
    }
    metricsDiv.innerHTML = '';
    for (const [sensor, data] of Object.entries(sensorGroups)) {
        // Skip rendering if sensor is not selected
        if (selectedSensors[sensor] === false) continue;
        if (!data.length) continue;
        const latest = data[data.length - 1];
        const value = latest.value;
        const timestamp = moment(latest.time).format('DD-MM-YYYY HH:mm:ss');
        const unit = getUnit(sensor);
        const icon = getSensorIcon(sensor);
        const sensorName = mapLang(sensor);
        const displayValue = unit ? `${value.toFixed(2)} ${unit}` : value;

        // Thêm kết quả chẩn đoán
        let diagnosis = '';
        let diagnosisClass = '';
        let diagnosisIcon = '';
        if (sensor.toUpperCase() === 'ECG') {
            const oneMinuteAgo = moment(latest.time).subtract(1, 'minute');
            const ecgArray = data.filter(d => moment(d.time).isSameOrAfter(oneMinuteAgo)).map(d => d.value);
            if (ecgArray.length > 0) {
                diagnosis = 'Đang phân tích...';
                analyzeECG(ecgArray).then(res => {
                    let resultText = '';
                    if (res && !res.error) {
                        resultText = `🔎 Kết quả: <span class="font-bold">${mapLang(res.class_name) || res.class_name}</span> (Độ tin cậy: <span class="font-bold">${(res.confidence * 100).toFixed(1)}%</span>)`;
                    } else {
                        const errorMessage = res.error ? ` (Lỗi: ${res.error})` : '';
                        resultText = `Không phân tích được ECG${errorMessage}`;
                    }
                    const cardDiv = metricsDiv.querySelector(`[data-sensor="${sensor}"] .diagnosis`);
                    if (cardDiv) cardDiv.innerHTML = resultText;
                }).catch(err => {
                    const cardDiv = metricsDiv.querySelector(`[data-sensor="${sensor}"] .diagnosis`);
                    if (cardDiv) cardDiv.innerHTML = `Không phân tích được ECG (Lỗi hệ thống: ${err.message || err})`;
                    console.error('Error during ECG analysis:', err);
                });
            } else {
                diagnosis = 'Không đủ dữ liệu ECG 1 phút gần nhất';
            }
        } else if (sensor.toUpperCase() === 'BPM') {
            const result = analyzeBPM(value);
            if (result === 'Normal BPM') {
                diagnosis = 'Nhịp tim bình thường';
                diagnosisClass = 'text-green-700';
                diagnosisIcon = '✅';
            } else {
                diagnosis = mapLang(result);
                diagnosisClass = 'text-red-600';
                diagnosisIcon = '⚠️';
            }
        } else if (sensor.toUpperCase() === 'SPO2') {
            const result = analyzeSpO2(value);
            if (result === 'Normal SpO2') {
                diagnosis = 'SpO2 bình thường';
                diagnosisClass = 'text-green-700';
                diagnosisIcon = '✅';
            } else {
                diagnosis = mapLang(result);
                diagnosisClass = 'text-red-600';
                diagnosisIcon = '⚠️';
            }
        } else if (sensor.toUpperCase() === 'TEMP') {
            const result = analyzeTemp(value);
            if (result === 'Normal Temperature') {
                diagnosis = 'Nhiệt độ bình thường';
                diagnosisClass = 'text-green-700';
                diagnosisIcon = '✅';
            } else {
                diagnosis = mapLang(result);
                diagnosisClass = 'text-red-600';
                diagnosisIcon = '⚠️';
            }
        }

        const card = `
            <div class="bg-white p-4 rounded-lg shadow-md border border-gray-200" data-sensor="${sensor}">
                <h3 class="text-lg font-semibold">${icon} ${sensorName}</h3>
                <p class="text-2xl font-bold">${displayValue}</p>
                <p class="text-sm text-gray-500">🕒 ${timestamp}</p>
                <p class="mt-2 font-semibold diagnosis ${diagnosisClass}">
                    ${diagnosis ? `${diagnosisIcon} ${diagnosis}` : ''}
                </p>
            </div>
        `;
        metricsDiv.innerHTML += card;
    }
}

export function renderCharts(sensorGroups) {
    if (isDebugEnabled) {
        console.log('[renderCharts]', sensorGroups);
    }
    const chartsDiv = document.getElementById('charts');
    chartsDiv.innerHTML = '';

    for (const [sensor, data] of Object.entries(sensorGroups)) {
        // Skip rendering if sensor is not selected
        if (selectedSensors[sensor] === false) continue;
        if (!data.length) continue;

        const container = document.createElement('div');
        container.className = 'bg-white p-4 rounded-lg shadow-md mt-4';

        const title = document.createElement('h3');
        title.className = 'text-lg font-semibold';
        title.innerHTML = `${getSensorIcon(sensor)} ${mapLang(sensor)}`;
        container.appendChild(title);

        const canvas = document.createElement('canvas');
        const canvasId = `chart-${sensor}`;
        canvas.id = canvasId;
        container.appendChild(canvas);

        chartsDiv.appendChild(container);

        const ctx = canvas.getContext('2d');
        if (typeof Chart !== 'undefined') {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => moment(d.time).format('HH:mm:ss')),
                    datasets: [{
                        label: mapLang(sensor),
                        data: data.map(d => d.value),
                        fill: false,
                        borderColor: '#3b82f6', // Blue color
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: 'Thời điểm' } },
                        y: { title: { display: true, text: getUnit(sensor) } }
                    }
                }
            });
        } else {
            console.error('Chart.js not loaded!');
        }
    }
}

const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
const sidebar = document.getElementById('sidebar-container');
const mainContent = document.querySelector('main');

toggleSidebarBtn.addEventListener('click', () => {
    const isSidebarHidden = sidebar.classList.toggle('sidebar-hidden');
    toggleSidebarBtn.classList.toggle('button-hidden', isSidebarHidden);
    toggleSidebarBtn.textContent = isSidebarHidden ? '☰' : '☰';
    if (isSidebarHidden) {
        mainContent.style.marginLeft = '0';
    } else {
        mainContent.style.marginLeft = '16rem';
    }
});

// Customize button and modal event listeners
const customizeBtn = document.getElementById('customizeBtn');
const customizeModal = document.getElementById('customizeModal');
const cancelCustomize = document.getElementById('cancelCustomize');
const saveCustomize = document.getElementById('saveCustomize');

// Ensure sensorGroups is globally available or fetched dynamically
let sensorGroups = {}; // Example: Replace with actual sensor data fetching logic

document.addEventListener('DOMContentLoaded', () => {
    if (customizeBtn) {
        customizeBtn.addEventListener('click', () => {
            if (!customizeModal) {
                console.error('Element with ID "customizeModal" not found.');
            } else {
                // Populate sensor checkboxes
                renderSensorSelectionModal(sensorGroups);
                customizeModal.classList.remove('hidden');
            }
        });
    }

    if (cancelCustomize) {
        cancelCustomize.addEventListener('click', () => {
            if (customizeModal) {
                customizeModal.classList.add('hidden');
            } else {
                console.error('Element with ID "customizeModal" not found.');
            }
        });
    }

    if (saveCustomize) {
        saveCustomize.addEventListener('click', () => {
            saveSelectedSensors();
            if (customizeModal) {
                customizeModal.classList.add('hidden');
            } else {
                console.error('Element with ID "customizeModal" not found.');
            }
        });
    }
});

// Function to render sensor selection modal
function renderSensorSelectionModal(sensorGroups) {
    const checkboxesDiv = document.getElementById('sensorCheckboxes');
    if (!checkboxesDiv) {
        console.error('Element with ID "sensorCheckboxes" not found.');
        return;
    }
    checkboxesDiv.innerHTML = ''; // Clear existing checkboxes
    Object.keys(sensorGroups).forEach(sensor => {
        const isChecked = selectedSensors[sensor] !== false; // Default to true if not explicitly false
        const checkbox = `
            <div class="flex items-center">
                <input type="checkbox" id="sensor-${sensor}" value="${sensor}" ${isChecked ? 'checked' : ''} class="mr-2">
                <label for="sensor-${sensor}" class="text-gray-700">${getSensorIcon(sensor)} ${mapLang(sensor)}</label>
            </div>
        `;
        checkboxesDiv.innerHTML += checkbox;
    });
}

// Listen for sensor group updates to populate the modal
window.addEventListener('fetchSensorGroupsForModal', () => {
    const sensorGroups = window.sensorGroups || {}; // Assume sensorGroups is globally available
    renderSensorSelectionModal(sensorGroups);
});
