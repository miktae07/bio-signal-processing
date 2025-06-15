import { renderMetrics, renderCharts } from './render.js';
import { setGreeting, updateUserProfile, getUnit } from './utils.js';

let isLoading = false;

async function loadData() {
    if(isLoading) {
        console.log('Load data already in progress, skipping...');
        return;
    }
    isLoading = true;
    console.log('--- loadData start ---');
    const groups = await getSensorGroups();
    // console.log('[loadData] groups:', groups);
    const err = document.getElementById('error');
    if (!Object.keys(groups).length) {
        err.textContent = '⚠️ Chưa có dữ liệu từ Firebase!';
        err.classList.remove('hidden');
    } else {
        err.classList.add('hidden');
        console.log('--- renderMetrics start ---');
        await renderMetrics(groups);
        renderCharts(groups);
    }
    console.log('--- loadData end ---');
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded');
    setGreeting();
    updateUserProfile('user1'); // Default user
    document.getElementById('userSelect').addEventListener('change', (e) => {
        updateUserProfile(e.target.value);
    });
    loadData();
    let debounceTimeout;
    database.ref('/').on('value', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            console.log('Firebase updated');
            loadData();
        }, 3); // 3ms debounce
    });
});
