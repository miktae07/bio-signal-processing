 // Set default date and time
            function setDefaultDateTime() {
                const startDateInput = document.getElementById('startDate');
                const startTimeInput = document.getElementById('startTime');
                const endDateInput = document.getElementById('endDate');
                const endTimeInput = document.getElementById('endTime');

                const defaultStart = moment('2025-01-01T00:00:00+07:00');
                const defaultEnd = moment().utcOffset('+07:00');

                startDateInput.value = defaultStart.format('YYYY-MM-DD');
                startTimeInput.value = defaultStart.format('HH:mm');
                endDateInput.value = defaultEnd.format('YYYY-MM-DD');
                endTimeInput.value = defaultEnd.format('HH:mm');
            }

            // Populate sensor select options
            async function populateSensorSelect() {
                const sensorGroups = await getSensorGroups();
                const sensorSelect = document.getElementById('sensorSelect');
                sensorSelect.innerHTML = '';
                Object.keys(sensorGroups).forEach(sensor => {
                    const option = document.createElement('option');
                    option.value = sensor;
                    option.textContent = mapLang(sensor);
                    sensorSelect.appendChild(option);
                });
            }

            // Render history data
            async function renderHistoryData() {
                const startDate = document.getElementById('startDate').value;
                const startTime = document.getElementById('startTime').value;
                const endDate = document.getElementById('endDate').value;
                const endTime = document.getElementById('endTime').value;
                const selectedSensors = Array.from(document.getElementById('sensorSelect').selectedOptions).map(opt => opt.value);

                if (!startDate || !startTime || !endDate || !endTime || !selectedSensors.length) {
                    document.getElementById('error').textContent = '⚠️ Vui lòng chọn đầy đủ ngày, giờ và cảm biến!';
                    document.getElementById('error').classList.remove('hidden');
                    return;
                }

                const start = moment(`${startDate}T${startTime}:00+07:00`).toISOString();
                const end = moment(`${endDate}T${endTime}:00+07:00`).toISOString();

                const sensorGroups = await getSensorGroups();
                const historyContent = document.getElementById('historyContent');
                historyContent.innerHTML = '';
                document.getElementById('error').classList.add('hidden');

                if (!Object.keys(sensorGroups).length) {
                    document.getElementById('error').textContent = '⚠️ Không có dữ liệu lịch sử từ Firebase!';
                    document.getElementById('error').classList.remove('hidden');
                    return;
                }

                selectedSensors.forEach(sensor => {
                    const data = sensorGroups[sensor] || [];
                    const filteredData = data.filter(d => {
                        const time = moment(d.time);
                        return time.isSameOrAfter(start) && time.isSameOrBefore(end);
                    });

                    if (!filteredData.length) {
                        const noDataDiv = document.createElement('div');
                        noDataDiv.className = 'text-blue-600 mb-4';
                        noDataDiv.textContent = `Không có dữ liệu cho ${mapLang(sensor)} trong khoảng đã chọn.`;
                        historyContent.appendChild(noDataDiv);
                        return;
                    }

                    // Render Chart
                    const chartContainer = document.createElement('div');
                    chartContainer.className = 'bg-white p-4 rounded-lg shadow-md mt-4';
                    const chartTitle = document.createElement('h3');
                    chartTitle.className = 'text-lg font-semibold';
                    chartTitle.innerHTML = `${getSensorIcon(sensor)} ${mapLang(sensor)}`;
                    chartContainer.appendChild(chartTitle);

                    const canvas = document.createElement('canvas');
                    const canvasId = `chart-${sensor}`;
                    canvas.id = canvasId;
                    chartContainer.appendChild(canvas);
                    historyContent.appendChild(chartContainer);

                    const ctx = canvas.getContext('2d');
                    if (typeof Chart !== 'undefined') {
                        new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: filteredData.map(d => moment(d.time).format('HH:mm:ss')),
                                datasets: [{
                                    label: mapLang(sensor),
                                    data: filteredData.map(d => d.value),
                                    fill: false,
                                    borderColor: '#3b82f6',
                                    tension: 0.1
                                }]
                            },
                            options: {
                                responsive: true,
                                scales: {
                                    x: { title: { display: true, text: 'Thời điểm' } },
                                    y: { title: { display: true, text: getUnit(sensor) } }
                                },
                                plugins: {
                                    title: {
                                        display: true,
                                        text: `Dữ liệu ${mapLang(sensor)} từ ${moment(start).format('DD-MM-YYYY HH:mm')} đến ${moment(end).format('DD-MM-YYYY HH:mm')}`
                                    }
                                }
                            }
                        });
                    }

                    // Render Table
                    const tableContainer = document.createElement('div');
                    tableContainer.className = 'bg-white p-4 rounded-lg shadow-md mt-4';
                    const tableTitle = document.createElement('h3');
                    tableTitle.className = 'text-lg font-semibold mb-2';
                    tableTitle.textContent = `Bảng dữ liệu ${mapLang(sensor)}`;
                    tableContainer.appendChild(tableTitle);

                    const table = document.createElement('table');
                    table.className = 'w-full border-collapse';
                    table.innerHTML = `
                        <thead>
                            <tr class="bg-gray-200">
                                <th class="border p-2">Thời gian</th>
                                <th class="border p-2">Giá trị</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${filteredData.map(d => `
                                <tr>
                                    <td class="border p-2">${moment(d.time).format('DD-MM-YYYY HH:mm:ss')}</td>
                                    <td class="border p-2">${d.value}${getUnit(sensor)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    `;
                    tableContainer.appendChild(table);
                    historyContent.appendChild(tableContainer);

                    // Download CSV Button
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200 mt-2';
                    downloadBtn.textContent = `📥 Tải dữ liệu ${mapLang(sensor)} dưới dạng CSV`;
                    downloadBtn.onclick = () => {
                        const csvContent = `time,value\n${filteredData.map(d => `${moment(d.time).format('YYYY-MM-DD HH:mm:ss')},${d.value}`).join('\n')}`;
                        const blob = new Blob([csvContent], { type: 'text/csv' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `data_${sensor}_${moment(start).format('YYYYMMDD_HHmm')}_${moment(end).format('YYYYMMDD_HHmm')}.csv`;
                        a.click();
                        URL.revokeObjectURL(url);
                    };
                    tableContainer.appendChild(downloadBtn);
                });
            }

            // Initialize
            document.addEventListener('DOMContentLoaded', () => {
                setGreeting();
                updateUserProfile('user1');
                document.getElementById('userSelect').addEventListener('change', (e) => {
                    updateUserProfile(e.target.value);
                });
                setDefaultDateTime();
                populateSensorSelect();
                document.getElementById('loadDataBtn').addEventListener('click', renderHistoryData);
            });