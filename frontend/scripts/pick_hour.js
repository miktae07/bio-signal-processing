import { renderMetrics, renderCharts } from './render.js';

// Global variable to store the current time filter
let currentTimeFilter = {
  type: 'recent', // 'recent' or 'specific'
  recentValue: 1,
  recentUnit: 'hours',
  specificStart: null,
  specificEnd: null
};

// Fallback for getSensorGroups if not available
async function getSensorGroups() {
  try {
    if (typeof window.getSensorGroups === 'function') {
      return await window.getSensorGroups();
    }
    console.warn('getSensorGroups not defined, returning empty object');
    return {};
  } catch (error) {
    console.error('Error fetching sensor groups:', error);
    return {};
  }
}

// Function to populate time options (every 5 minutes)
function populateTimeOptions(selectElement) {
  const times = [];
  for (let h = 0; h < 24; h++) {
    for (let m = 0; m < 60; m += 5) {
      const time = moment({ hour: h, minute: m }).format('HH:mm');
      times.push(time);
    }
  }
  selectElement.innerHTML = '';
  times.forEach(time => {
    const option = document.createElement('option');
    option.value = time;
    option.textContent = time;
    selectElement.appendChild(option);
  });
}

// Function to show the time filter modal
function showTimeFilterModal() {
  console.log('Rendering time filter modal');
  // Remove any existing modal to prevent duplicates
  const existingModal = document.getElementById('time-filter-modal');
  if (existingModal) existingModal.remove();

  const modal = document.createElement('div');
  modal.id = 'time-filter-modal';
  modal.className = 'fixed z-50'; // Use fixed for overlay, but position absolutely within container
  modal.innerHTML = `
    <div class="modal-content bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
      <h2 class="text-xl font-semibold mb-4">⏰ Lọc Theo Thời Điểm</h2>
      <!-- Tabs -->
      <div class="flex border-b mb-4">
        <button id="recent-tab" class="px-4 py-2 font-semibold text-blue-600 border-b-2 border-blue-600">Gần Đây</button>
        <button id="specific-tab" class="px-4 py-2 font-semibold text-gray-600">Cụ Thể</button>
      </div>
      <!-- Recent Tab Content -->
      <div id="recent-content" class="tab-content">
        <div class="flex items-center gap-4">
          <input type="number" id="recent-value" min="1" value="1" class="w-20 p-2 border rounded backend-input">
          <select id="recent-unit" class="p-2 border rounded backend-input">
            <option value="minutes">Phút</option>
            <option value="hours" selected>Giờ</option>
            <option value="days">Ngày</option>
            <option value="months">Tháng</option>
          </select>
        </div>
      </div>
      <!-- Specific Tab Content -->
      <div id="specific-content" class="tab-content hidden">
        <div class="specific-main grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium">📅 Từ ngày</label>
            <input type="date" id="start-date" class="w-full p-2 border rounded backend-input">
          </div>
          <div>
            <label class="block text-sm font-medium">⏰ Từ giờ</label>
            <select id="start-time" class="w-full p-2 border rounded backend-input"></select>
          </div>
          <div>
            <label class="block text-sm font-medium">📅 Đến ngày</label>
            <input type="date" id="end-date" class="w-full p-2 border rounded backend-input">
          </div>
          <div>
            <label class="block text-sm font-medium">⏰ Đến giờ</label>
            <select id="end-time" class="w-full p-2 border rounded backend-input"></select>
          </div>
        </div>
      </div>
      <!-- Modal Buttons -->
      <div class="flex justify-end gap-2 mt-6">
        <button id="cancel-time-filter" class="btn-cancel px-4 py-2">Hủy</button>
        <button id="save-time-filter" class="btn-submit px-4 py-2">Lưu</button>
      </div>
    </div>
  `;

  // Append modal to settings-container for absolute positioning
  const settingsContainer = document.getElementById('settings-container');
  if (settingsContainer) {
    settingsContainer.appendChild(modal);
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
      const rect = settingsBtn.getBoundingClientRect();
      modal.style.position = 'absolute';
      modal.style.top = `${rect.bottom + 10}px`; // 10px below settings button
      modal.style.right = '0'; // Align to the right of settings-container
    }
  } else {
    console.error('Settings container not found!');
    document.body.appendChild(modal); // Fallback to body if container not found
  }

  // Populate time options
  const startTimeSelect = document.getElementById('start-time');
  const endTimeSelect = document.getElementById('end-time');
  populateTimeOptions(startTimeSelect);
  populateTimeOptions(endTimeSelect);

  // Set default values
  const startDateInput = document.getElementById('start-date');
  const endDateInput = document.getElementById('end-date');
  startDateInput.value = moment().subtract(1, 'days').format('YYYY-MM-DD');
  endDateInput.value = moment().format('YYYY-MM-DD');
  startTimeSelect.value = '00:00';
  endTimeSelect.value = '23:59';

  // Tab switching logic
  const recentTab = document.getElementById('recent-tab');
  const specificTab = document.getElementById('specific-tab');
  const recentContent = document.getElementById('recent-content');
  const specificContent = document.getElementById('specific-content');

  recentTab.addEventListener('click', () => {
    recentTab.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
    specificTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
    recentTab.classList.remove('text-gray-600');
    specificTab.classList.add('text-gray-600');
    recentContent.classList.remove('hidden');
    specificContent.classList.add('hidden');
  });

  specificTab.addEventListener('click', () => {
    specificTab.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
    recentTab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
    specificTab.classList.remove('text-gray-600');
    recentTab.classList.add('text-gray-600');
    specificContent.classList.remove('hidden');
    recentContent.classList.add('hidden');
  });

  // Enhance buttons with hover and active effects
  const cancelBtn = document.getElementById('cancel-time-filter');
  const saveBtn = document.getElementById('save-time-filter');

  cancelBtn.addEventListener('mouseover', () => {
    cancelBtn.style.backgroundColor = '#cbd5e1';
    cancelBtn.style.transform = 'scale(1.05)';
    cancelBtn.style.transition = 'all 0.2s ease';
  });

  cancelBtn.addEventListener('mouseout', () => {
    cancelBtn.style.backgroundColor = '';
    cancelBtn.style.transform = '';
  });

  cancelBtn.addEventListener('mousedown', () => {
    cancelBtn.style.boxShadow = 'inset 0 2px 4px rgba(0, 0, 0, 0.1)';
    cancelBtn.style.backgroundColor = '#b0b9c5';
  });

  cancelBtn.addEventListener('mouseup', () => {
    cancelBtn.style.boxShadow = '';
    cancelBtn.style.backgroundColor = '';
  });

  saveBtn.addEventListener('mouseover', () => {
    saveBtn.style.backgroundColor = '#2563eb';
    saveBtn.style.transform = 'scale(1.05)';
    saveBtn.style.transition = 'all 0.2s ease';
  });

  saveBtn.addEventListener('mouseout', () => {
    saveBtn.style.backgroundColor = '';
    saveBtn.style.transform = '';
  });

  saveBtn.addEventListener('mousedown', () => {
    saveBtn.style.boxShadow = 'inset 0 2px 4px rgba(0, 0, 0, 0.1)';
    saveBtn.style.backgroundColor = '#1d4ed8';
  });

  saveBtn.addEventListener('mouseup', () => {
    saveBtn.style.boxShadow = '';
    saveBtn.style.backgroundColor = '';
  });

  // Cancel button
  cancelBtn.addEventListener('click', () => {
    console.log('Time filter modal cancelled');
    modal.remove();
  });

  // Save button
  saveBtn.addEventListener('click', async () => {
    console.log('Saving time filter');
    if (recentContent.classList.contains('hidden')) {
      const startDate = document.getElementById('start-date').value;
      const startTime = document.getElementById('start-time').value;
      const endDate = document.getElementById('end-date').value;
      const endTime = document.getElementById('end-time').value;

      if (!startDate || !startTime || !endDate || !endTime) {
        alert('Vui lòng chọn đầy đủ ngày và giờ!');
        return;
      }

      currentTimeFilter = {
        type: 'specific',
        recentValue: null,
        recentUnit: null,
        specificStart: moment.tz(`${startDate} ${startTime}:00`, 'Asia/Ho_Chi_Minh').toISOString(),
        specificEnd: moment.tz(`${endDate} ${endTime}:00`, 'Asia/Ho_Chi_Minh').toISOString()
      };
    } else {
      const recentValue = parseInt(document.getElementById('recent-value').value);
      const recentUnit = document.getElementById('recent-unit').value;

      if (!recentValue || recentValue < 1) {
        alert('Vui lòng nhập số lượng thời gian hợp lệ!');
        return;
      }

      currentTimeFilter = {
        type: 'recent',
        recentValue,
        recentUnit,
        specificStart: null,
        specificEnd: null
      };
    }

    modal.remove();
    await applyTimeFilter();
  });

  // Close modal when clicking outside
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      console.log('Time filter modal closed via overlay click');
      modal.remove();
    }
  });
}

// Function to apply the time filter and render metrics/charts
async function applyTimeFilter() {
  console.log('Applying time filter:', currentTimeFilter);
  try {
    let start, end;
    if (currentTimeFilter.type === 'recent') {
      end = moment().toISOString();
      start = moment().subtract(currentTimeFilter.recentValue, currentTimeFilter.recentUnit).toISOString();
    } else {
      start = currentTimeFilter.specificStart;
      end = currentTimeFilter.specificEnd;
    }

    const sensorGroups = await getSensorGroups();
    const filteredSensorGroups = {};

    for (const [sensor, data] of Object.entries(sensorGroups)) {
      filteredSensorGroups[sensor] = data.filter(d => {
        const time = moment(d.time);
        return time.isSameOrAfter(start) && time.isSameOrBefore(end);
      });
    }

    await renderMetrics(filteredSensorGroups);
    renderCharts(filteredSensorGroups);
  } catch (error) {
    console.error('Error applying time filter:', error);
    const metricsDiv = document.getElementById('metrics');
    if (metricsDiv) {
      metricsDiv.innerHTML = '<p class="text-red-600">⚠️ Lỗi khi lọc dữ liệu!</p>';
    }
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing pick_hour.js');
  const settingsDropdown = document.getElementById('settings-dropdown');
  if (settingsDropdown) {
    const timeFilterBtn = document.createElement('button');
    timeFilterBtn.id = 'time-filter-btn';
    timeFilterBtn.className = 'block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100';
    timeFilterBtn.textContent = 'Lọc Theo Thời Điểm';
    timeFilterBtn.addEventListener('click', () => {
      console.log('Time filter button clicked');
      settingsDropdown.classList.add('hidden');
      showTimeFilterModal();
    });
    settingsDropdown.appendChild(timeFilterBtn);
  } else {
    console.error('Settings dropdown not found!');
  }

  // Apply default filter (last 1 hour)
  applyTimeFilter();
});
