async function renderMetrics(sensorGroups) {
    console.log('[renderMetrics]', sensorGroups);
    const metricsDiv = document.getElementById('metrics');
    metricsDiv.innerHTML = '';
    for (const [sensor, data] of Object.entries(sensorGroups)) {
        if (!data.length) continue;
        const latest = data[data.length - 1];
        const value = latest.value;
        const timestamp = moment(latest.time).format('DD-MM-YYYY HH:mm:ss');
        const unit = getUnit(sensor);
        const icon = getSensorIcon(sensor);
        const sensorName = mapLang(sensor);
        const displayValue = unit ? `${value.toFixed(2)} ${unit}` : value;
        const card = `
            <div class="bg-white p-4 rounded-lg shadow-md border border-gray-200">
                <h3 class="text-lg font-semibold">${icon} ${sensorName}</h3>
                <p class="text-2xl font-bold">${displayValue}</p>
                <p class="text-sm text-gray-500">🕒 ${timestamp}</p>
            </div>
        `;
        metricsDiv.innerHTML += card;
    }
}

function renderCharts(sensorGroups) {
    console.log('[renderCharts]', sensorGroups);
    const chartsDiv = document.getElementById('charts');
    chartsDiv.innerHTML = '';

    for (const [sensor, data] of Object.entries(sensorGroups)) {
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
                        borderColor: '#3b82f6', // Màu xanh dương
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
            console.error('Chart.js chưa được load!');
        }
    }
}