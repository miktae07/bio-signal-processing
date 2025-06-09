import analyzeBPM from './data_processing/analyzeBPM.js';
import analyzeSpO2 from './data_processing/analyzeSpO2.js';
import analyzeECG from './data_processing/analyzeECG.js';
import analyzeTemp from './data_processing/analyzeTemp.js';

console.log('analysis.js loaded');

console.log(analyzeBPM(55)); // Output: Bradycardia
console.log(analyzeSpO2(92)); // Output: Mild respiratory failure
console.log(analyzeECG(120)); // Output: Abnormal
console.log(analyzeTemp(35)); // Output: Hypothermia

// Populate time options (every 5 minutes)
function populateTimeOptions() {
    const times = [];
    for (let h = 0; h < 24; h++) {
        for (let m = 0; m < 60; m += 5) {
            const time = moment({ hour: h, minute: m }).format('HH:mm');
            times.push(time);
        }
    }
    const startTimeSelect = document.getElementById('startTime');
    const endTimeSelect = document.getElementById('endTime');
    startTimeSelect.innerHTML = '';
    endTimeSelect.innerHTML = '';
    times.forEach(time => {
        const option = document.createElement('option');
        option.value = time;
        option.textContent = time;
        startTimeSelect.appendChild(option.cloneNode(true));
        endTimeSelect.appendChild(option.cloneNode(true));
    });
    startTimeSelect.value = '00:00';
    endTimeSelect.value = '23:59';
}

// Populate signal select options
async function populateSignalSelect() {
    try {
        const sensorGroups = await getSensorGroups();
        const signalSelect = document.getElementById('signalSelect');
        signalSelect.innerHTML = '';
        if (!sensorGroups || Object.keys(sensorGroups).length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Không có tín hiệu';
            option.disabled = true;
            signalSelect.appendChild(option);
            return;
        }
        Object.keys(sensorGroups).forEach(sensor => {
            const option = document.createElement('option');
            option.value = sensor;
            option.textContent = mapLang(sensor) || sensor;
            signalSelect.appendChild(option);
        });
        // Chọn mặc định cái đầu tiên nếu có
        if (signalSelect.options.length > 0) {
            signalSelect.options[0].selected = true;
        }
    } catch (error) {
        console.error('Lỗi khi lấy dữ liệu cảm biến:', error);
        const signalSelect = document.getElementById('signalSelect');
        signalSelect.innerHTML = '';
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'Lỗi tải dữ liệu';
        option.disabled = true;
        signalSelect.appendChild(option);
    }
}

// Process signal data
function processSignal(sensor, data, start, end) {
    const filteredData = data.filter(d => {
        const time = moment(d.time);
        return time.isSameOrAfter(start) && time.isSameOrBefore(end);
    });
    const exportData = [];
    const summary = { min: Infinity, max: -Infinity, mean: 0, count: 0 };

    filteredData.forEach(d => {
        let analysisResult;
        switch (sensor.toUpperCase()) {
            case 'BPM': 
                analysisResult = mapLang(analyzeBPM(d.value)); 
                break;
            case 'SPO2': 
                analysisResult = mapLang(analyzeSpO2(d.value)); 
                break;
            case 'ECG': 
                analysisResult = mapLang(analyzeECG(d.value)); 
                break;
            case 'TEMP': 
                analysisResult = mapLang(analyzeTemp(d.value)); 
                break;
            default: 
                analysisResult = mapLang('Unknown');
        }
        exportData.push({
            type: mapLang(sensor) || sensor,
            timestamp: moment(d.time).format('YYYY-MM-DD HH:mm:ss'),
            value: d.value,
            result: analysisResult
        });
        summary.min = Math.min(summary.min, d.value);
        summary.max = Math.max(summary.max, d.value);
        summary.mean += d.value;
        summary.count++;
    });

    if (summary.count > 0) {
        summary.mean /= summary.count;
    } else {
        summary.min = summary.max = summary.mean = 0;
    }

    return { exportData, summary };
}

// Render analysis data
async function renderAnalysisData() {
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const endDate = document.getElementById('endDate').value;
    const endTime = document.getElementById('endTime').value;
    const signalSelect = document.getElementById('signalSelect');
    const selectedSignals = Array.from(signalSelect.selectedOptions).map(opt => opt.value);

    if (!startDate || !startTime || !endDate || !endTime || selectedSignals.length === 0) {
        document.getElementById('error').textContent = '⚠️ Vui lòng chọn đầy đủ ngày, giờ và ít nhất một tín hiệu!';
        document.getElementById('error').classList.remove('hidden');
        return;
    }

    const start = moment.tz(`${startDate} ${startTime}:00`, 'Asia/Ho_Chi_Minh').toISOString();
    const end = moment.tz(`${endDate} ${endTime}:00`, 'Asia/Ho_Chi_Minh').toISOString();

    try {
        const sensorGroups = await getSensorGroups();
        const analysisContent = document.getElementById('analysisContent');
        analysisContent.innerHTML = '';
        document.getElementById('error').classList.add('hidden');

        if (!sensorGroups || Object.keys(sensorGroups).length === 0) {
            document.getElementById('error').textContent = '⚠️ Không tìm thấy dữ liệu để phân tích!';
            document.getElementById('error').classList.remove('hidden');
            return;
        }

        const filteredGroups = {};
        const exportData = [];
        const summaryRows = [];

        selectedSignals.forEach(sensor => {
            if (sensor in sensorGroups) {
                const data = sensorGroups[sensor];
                const { exportData: signalExport, summary } = processSignal(sensor, data, start, end);
                exportData.push(...signalExport);
                summaryRows.push({
                    type: mapLang(sensor) || sensor,
                    min: summary.min.toFixed(2),
                    max: summary.max.toFixed(2),
                    mean: summary.mean.toFixed(2),
                    result: signalExport.length ? signalExport[0].result : 'No data'
                });
                filteredGroups[sensor] = data.filter(d => {
                    const time = moment(d.time);
                    return time.isSameOrAfter(start) && time.isSameOrBefore(end);
                });
            }
        });

        if (Object.keys(filteredGroups).length > 0) {
            const chartContainer = document.createElement('div');
            chartContainer.className = 'bg-white p-4 rounded-lg shadow-md mt-4';
            const chartTitle = document.createElement('h2');
            chartTitle.className = 'text-xl font-semibold';
            chartTitle.textContent = '📈 Biểu đồ Phân Tích';
            chartContainer.appendChild(chartTitle);

            const canvas = document.createElement('canvas');
            const canvasId = 'analysisChart';
            canvas.id = canvasId;
            chartContainer.appendChild(canvas);
            analysisContent.appendChild(chartContainer);

            const ctx = canvas.getContext('2d');
            if (typeof Chart !== 'undefined') {
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: Object.values(filteredGroups).flat().map(d => moment(d.time).format('HH:mm:ss')),
                        datasets: Object.keys(filteredGroups).map((sensor, index) => ({
                            label: mapLang(sensor) || sensor,
                            data: filteredGroups[sensor].map(d => d.value),
                            fill: false,
                            borderColor: '#3b82f6',
                            tension: 0.1
                        }))
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Thời điểm' } },
                            y: { title: { display: true, text: 'Giá trị' } }
                        },
                        plugins: {
                            legend: { position: 'top' }
                        }
                    }
                });
            }
        } else {
            analysisContent.innerHTML = '<p class="text-blue-600">Không có dữ liệu để vẽ biểu đồ trong khoảng đã chọn.</p>';
        }

        if (exportData.length > 0) {
            const exportTable = document.createElement('div');
            exportTable.className = 'bg-white p-4 rounded-lg shadow-md mt-4';
            const tableTitle = document.createElement('h3');
            tableTitle.className = 'text-lg font-semibold mb-2';
            tableTitle.textContent = '📋 Bảng Kết Quả Phân Tích';
            exportTable.appendChild(tableTitle);

            const table = document.createElement('table');
            table.className = 'w-full border-collapse';
            table.innerHTML = `
                <thead>
                    <tr class="bg-gray-200">
                        <th class="border p-2">Loại Dữ Liệu</th>
                        <th class="border p-2">Thời gian</th>
                        <th class="border p-2">Giá trị</th>
                        <th class="border p-2">Kết quả Phân tích</th>
                    </tr>
                </thead>
                <tbody>
                    ${exportData.map(d => `
                        <tr>
                            <td class="border p-2">${d.type}</td>
                            <td class="border p-2">${d.timestamp}</td>
                            <td class="border p-2">${d.value}</td>
                            <td class="border p-2">${d.result}</td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
            exportTable.appendChild(table);
            analysisContent.appendChild(exportTable);

            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200 mt-2';
            downloadBtn.textContent = '📥 Tải về CSV';
            downloadBtn.onclick = () => {
                const csvContent = 'Data Type,Timestamp,Value,Analysis Result\n' + exportData.map(d => `${d.type},${d.timestamp},${d.value},${d.result}`).join('\n');
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ket_qua_phan_tich_${moment().format('YYYYMMDD_HHmmss')}.csv`;
                a.click();
                URL.revokeObjectURL(url);
            };
            exportTable.appendChild(downloadBtn);
        }

        if (summaryRows.length > 0) {
            const summaryTable = document.createElement('div');
            summaryTable.className = 'bg-white p-4 rounded-lg shadow-md mt-4';
            const summaryTitle = document.createElement('h3');
            summaryTitle.className = 'text-lg font-semibold mb-2';
            summaryTitle.textContent = '📊 Tổng hợp theo loại dữ liệu';
            summaryTable.appendChild(summaryTitle);

            const table = document.createElement('table');
            table.className = 'w-full border-collapse';
            table.innerHTML = `
                <thead>
                    <tr class="bg-gray-200">
                        <th class="border p-2">Loại Dữ Liệu</th>
                        <th class="border p-2">Min</th>
                        <th class="border p-2">Max</th>
                        <th class="border p-2">Mean</th>
                        <th class="border p-2">Kết quả Phân tích</th>
                    </tr>
                </thead>
                <tbody>
                    ${summaryRows.map(r => `
                        <tr>
                            <td class="border p-2">${r.type}</td>
                            <td class="border p-2">${r.min}</td>
                            <td class="border p-2">${r.max}</td>
                            <td class="border p-2">${r.mean}</td>
                            <td class="border p-2">${r.result}</td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
            summaryTable.appendChild(table);
            analysisContent.appendChild(summaryTable);
        }
    } catch (error) {
        console.error('Lỗi khi render dữ liệu phân tích:', error);
        document.getElementById('error').textContent = '⚠️ Đã xảy ra lỗi khi phân tích dữ liệu!';
        document.getElementById('error').classList.remove('hidden');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setGreeting();
    updateUserProfile('user1');
    document.getElementById('userSelect').addEventListener('change', (e) => {
        updateUserProfile(e.target.value);
    });
    document.getElementById('startDate').value = '2025-01-01';
    document.getElementById('endDate').value = moment().format('YYYY-MM-DD'); // Mặc định đến ngày hiện tại
    populateTimeOptions();
    populateSignalSelect();
    document.getElementById('analyzeBtn').addEventListener('click', renderAnalysisData);
});

const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
const sidebar = document.getElementById('sidebar');

toggleSidebarBtn.addEventListener('click', () => {
    const isSidebarHidden = sidebar.classList.toggle('sidebar-hidden');
    toggleSidebarBtn.classList.toggle('button-hidden', isSidebarHidden);
    if (isSidebarHidden) {
        toggleSidebarBtn.textContent = '☰'; // Update button text when sidebar is closed
    } else {
        toggleSidebarBtn.textContent = '☰'; // Update button text when sidebar is open
    }
});
