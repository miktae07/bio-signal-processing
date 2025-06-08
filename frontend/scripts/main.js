async function loadData() {
    console.log('--- loadData start ---');
    const groups = await getSensorGroups();
    console.log('[loadData] groups:', groups);
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
    database.ref('/').on('value', () => { console.log('Firebase updated'); loadData(); });
    document.getElementById('reloadBtn').addEventListener('click', loadData);
});