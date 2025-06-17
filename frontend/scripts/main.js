import { renderMetrics, renderCharts } from './render.js';
import { setGreeting, updateUserProfile } from './utils.js';

let isLoading = false;

async function loadData() {
    if (isLoading) {
        console.log('Load data already in progress, skipping...');
        return;
    }
    isLoading = true;

    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) loadingOverlay.classList.remove('hidden');

    const metricsDiv = document.getElementById('metrics');
    const chartsDiv = document.getElementById('charts');

    // ✅ Ghi trực tiếp custom spinner vào metrics & charts
    const customSpinner = `
        <div class="col-span-full text-center text-blue-500">
            <div class="flex justify-center items-center gap-2">
                <div class="custom-spinner"></div>
                <span>Đang tải dữ liệu...</span>
            </div>
        </div>
    `;

    metricsDiv.innerHTML = customSpinner;
    chartsDiv.innerHTML = customSpinner.replace('Đang tải dữ liệu...', 'Đang tải biểu đồ...');

    console.log('--- loadData start ---');
    const groups = await getSensorGroups();
    window.sensorGroups = groups;

    const err = document.getElementById('error');
    if (!Object.keys(groups).length) {
        err.textContent = '⚠️ Chưa có dữ liệu từ Firebase!';
        err.classList.remove('hidden');
        metricsDiv.innerHTML = '';
        chartsDiv.innerHTML = '';
    } else {
        err.classList.add('hidden');
        console.log('--- renderMetrics start ---');
        await renderMetrics(groups);
        renderCharts(groups);
    }

    console.log('--- loadData end ---');
    if (loadingOverlay) loadingOverlay.classList.add('hidden');
    isLoading = false;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded');
    setGreeting();
    updateUserProfile('user1');

    document.getElementById('userSelect')?.addEventListener('change', (e) => {
        updateUserProfile(e.target.value);
    });

    loadData();

    let debounceTimeout;
    database.ref('/').on('value', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            console.log('Firebase updated');
            loadData();
        }, 3);
    });

    window.addEventListener('updateSensorDisplay', () => {
        if (!window.sensorGroups) {
            console.error('Không có dữ liệu sensorGroups để cập nhật hiển thị!');
            return;
        }
        renderMetrics(window.sensorGroups);
        renderCharts(window.sensorGroups);
    });
});
