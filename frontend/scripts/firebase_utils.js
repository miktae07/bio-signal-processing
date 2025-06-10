// Global debug flag
let isDebugEnabled = false;

// Function to enable debug mode
window.allowDebug = function() {
    isDebugEnabled = true;
    console.log('Debug mode enabled');
};

const firebaseConfig = {
    apiKey: "AIzaSyDneFPslsW4O0-3TGLV5yAWFvGaRbdttuY",
    authDomain: "esp32-9c871.firebaseapp.com",
    databaseURL: "https://esp32-9c871-default-rtdb.firebaseio.com",
    projectId: "esp32-9c871",
    storageBucket: "esp32-9c871.firebasestorage.app",
    messagingSenderId: "321309512205",
    appId: "1:321309512205:web:e5e5f809b56b0ac125bb44",
    measurementId: "G-7RY1158KD2"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

function parseNode(sensor, node, pathKeys) {
    if (isDebugEnabled) {
        console.debug(`[parseNode] sensor=${sensor}, pathKeys=${JSON.stringify(pathKeys)}`);
    }
    let records = [];
    if (node && typeof node === 'object') {
        for (const [key, value] of Object.entries(node)) {
            records = records.concat(parseNode(sensor, value, [...pathKeys, key]));
        }
    } else {
        try {
            let ts;
            if (pathKeys.length >= 6) {
                ts = `${pathKeys[0]}-${pathKeys[1].padStart(2, '0')}-${pathKeys[2].padStart(2, '0')} ` +
                     `${pathKeys[3].padStart(2, '0')}:${pathKeys[4].padStart(2, '0')}:${pathKeys[5].padStart(2, '0')}`;
            } else {
                if (isDebugEnabled) {
                    console.warn(`[parseNode] pathKeys ngắn, dùng hiện tại:`, pathKeys);
                }
                ts = moment().toISOString();
            }
            const baseTime = moment(ts);
            if (sensor === 'ECG') {
                const vals = String(node).match(/-?\d+/g)?.map(Number) || [];
                vals.forEach((val, i) => {
                    records.push({ sensor, time: baseTime.clone().add(i * 4, 'ms').toISOString(), value: val });
                });
            } else {
                const val = isNaN(parseFloat(node)) ? node : parseFloat(node);
                records.push({ sensor, time: baseTime.toISOString(), value: val });
            }
        } catch (e) {
            console.error(`[parseNode] lỗi parse sensor=${sensor}, pathKeys=${pathKeys}:`, e);
        }
    }
    return records;
}

async function getSensorGroups() {
    try {
        const snapshot = await database.ref('/').once('value');
        const data = snapshot.val();
        if (isDebugEnabled) {
            console.log('[getSensorGroups] raw:', data);
        }
        if (!data || typeof data !== 'object') return {};
        let all = [];
        for (const [sensor, node] of Object.entries(data)) {
            const recs = parseNode(sensor, node, []);
            if (isDebugEnabled) {
                console.log(`[parsed ${sensor}]`, recs);
            }
            all = all.concat(recs);
        }
        if (!all.length) return {};
        const grouped = all.reduce((acc, r) => {
            acc[r.sensor] = acc[r.sensor] || [];
            acc[r.sensor].push(r);
            return acc;
        }, {});
        Object.values(grouped).forEach(arr => arr.sort((a, b) => new Date(a.time) - new Date(b.time)));
        if (isDebugEnabled) {
            console.log('[getSensorGroups] grouped keys:', Object.keys(grouped));
        }
        return grouped;
    } catch (e) {
        console.error('[getSensorGroups] lỗi:', e);
        return {};
    }
}