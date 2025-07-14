import { toggleTheme, getTheme } from './theme.js';
import { setBackendAddress } from './backend_config.js';
import { renderSensorSelectionModal, saveSelectedSensors } from './render.js';

document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('change-theme-btn');
    const settingsDropdown = document.getElementById('settings-dropdown');
    const settingsBtn = document.getElementById('settings-btn');
    const connectBtn = document.getElementById('connect-backend-btn');
    const selectDataBtn = document.getElementById('select-data-btn');
    const backendModal = document.getElementById('backend-modal');
    const sensorModal = document.getElementById('sensor-modal');
    const cancelBtn = document.getElementById('cancel-backend-btn');
    const submitBtn = document.getElementById('submit-backend-btn');
    const cancelSensorBtn = document.getElementById('cancel-sensor-btn');
    const saveSensorBtn = document.getElementById('save-sensor-btn');
    const addressInput = document.getElementById('backend-address');
    const sensorCheckboxes = document.getElementById('sensorCheckboxes');
    const timeFilterBtn = document.getElementById('time-filter-btn');


    // Language data
    const languageData = {
        vi: {
            themeLabelLight: "Dark Mode",
            themeLabelDark: "Light Mode",
            connectBackend: "Kết Nối Backend",
            selectData: "Chọn Dữ Liệu",
            languageLabel: "Ngôn Ngữ",
            currentLanguage: "Tiếng Việt",
            saveSensors: "Lưu",
            cancel: "Hủy",
            noSensors: "Không có cảm biến nào khả dụng",
            filterby: "Lọc theo thời điểm",
        },
        en: {
            themeLabelLight: "Dark Mode",
            themeLabelDark: "Light Mode",
            connectBackend: "Connect Backend",
            selectData: "Select Data Sources",
            languageLabel: "Language",
            currentLanguage: "English",
            saveSensors: "Save",
            cancel: "Cancel",
            noSensors: "No sensors available",
            filterby: "Filter by hour and minute",
        },
    };

    // Function to update language
    function updateLanguage(lang) {
        const data = languageData[lang] || languageData.vi; // Default to Vietnamese
        themeBtn.textContent = getTheme() === 'light'
            ? data.themeLabelLight
            : data.themeLabelDark;
        connectBtn.textContent = data.connectBackend;
        if (selectDataBtn) selectDataBtn.textContent = data.selectData;
        if (saveSensorBtn) saveSensorBtn.textContent = data.saveSensors;
        if (cancelSensorBtn) cancelSensorBtn.textContent = data.cancel;
        if (timeFilterBtn) timeFilterBtn.textContent = data.filterby;
        document.querySelector('label[for="language-select"]').textContent = data.languageLabel;
    }

    // Initialize language on page load
    const savedLang = localStorage.getItem('language') || 'vi'; // Default to Vietnamese

    // Function to update theme label
    function updateThemeLabel() {
        const theme = getTheme(); // 'light' or 'dark'
        themeBtn.textContent = theme === 'light'
            ? languageData[savedLang].themeLabelLight
            : languageData[savedLang].themeLabelDark;
    }

    // Initialize theme label
    updateThemeLabel();

    // Event listener for theme button
    themeBtn.addEventListener('click', () => {
        toggleTheme(); // Toggle theme
        updateThemeLabel(); // Update theme label
        settingsDropdown.classList.add('hidden'); // Hide dropdown
    });

    // Event listener for settings button
    settingsBtn.addEventListener('click', () => {
        settingsDropdown.classList.toggle('hidden');
    });

    // Event listener for backend connection button
    connectBtn.addEventListener('click', () => {
        settingsDropdown.classList.add('hidden');
        backendModal.classList.remove('hidden');
        backendModal.classList.add('flex');
    });

    // Event listener for select data sources button
    if (selectDataBtn) {
        selectDataBtn.addEventListener('click', async () => {
            settingsDropdown.classList.add('hidden');
            sensorModal.classList.remove('hidden');
            sensorModal.classList.add('flex');
            // Fetch sensor groups from Firebase
            try {
                if (!window.getSensorGroups) {
                    throw new Error('getSensorGroups is not defined');
                }
                const sensorGroups = await window.getSensorGroups();
                window.sensorGroups = sensorGroups; // Store in global variable
                if (Object.keys(sensorGroups).length === 0 && sensorCheckboxes) {
                    // Display message if no sensors are available
                    sensorCheckboxes.innerHTML = `<p class="text-gray-700">${languageData[savedLang].noSensors}</p>`;
                } else {
                    // Populate sensor checkboxes
                    renderSensorSelectionModal(sensorGroups);
                    // Thêm xử lý cho Select all / Deselect all
                    const selectAllBtn = document.getElementById('selectAllSensors');
                    const deselectAllBtn = document.getElementById('deselectAllSensors');
                    
                    if (selectAllBtn && deselectAllBtn) {
                        selectAllBtn.textContent = 'Chọn tất cả';
                        deselectAllBtn.textContent = 'Bỏ chọn tất cả';

                        selectAllBtn.addEventListener('click', () => {
                            document.querySelectorAll('#sensorCheckboxes input[type="checkbox"]').forEach(cb => cb.checked = true);
                        });
                        deselectAllBtn.addEventListener('click', () => {
                            document.querySelectorAll('#sensorCheckboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
                        });
                    }
                }
            } catch (error) {
                console.error('Error fetching sensor groups:', error);
                if (sensorCheckboxes) {
                    sensorCheckboxes.innerHTML = `<p class="text-red-600">${languageData[savedLang].noSensors}</p>`;
                }
            }
        });
    }

    // Event listener for cancel button in backend modal
    cancelBtn.addEventListener('click', () => {
        backendModal.classList.add('hidden');
        backendModal.classList.remove('flex');
    });

    // Event listener for submit button in backend modal
    submitBtn.addEventListener('click', () => {
        const address = addressInput.value.trim();
        if (address) setBackendAddress(address);
        backendModal.classList.add('hidden');
        backendModal.classList.remove('flex');
    });

    // Event listener for cancel button in sensor modal
    if (cancelSensorBtn) {
        cancelSensorBtn.addEventListener('click', () => {
            sensorModal.classList.add('hidden');
            sensorModal.classList.remove('flex');
        });
    }

    // Event listener for save button in sensor modal
    if (saveSensorBtn) {
        saveSensorBtn.addEventListener('click', () => {
            saveSelectedSensors();
            sensorModal.classList.add('hidden');
            sensorModal.classList.remove('flex');
        });
    }

    // Close backend modal when clicking outside the modal content
    backendModal.addEventListener('click', (e) => {
        if (e.target === backendModal) {
            backendModal.classList.add('hidden');
            backendModal.classList.remove('flex');
        }
    });

    // Close sensor modal when clicking outside the modal content
    if (sensorModal) {
        sensorModal.addEventListener('click', (e) => {
            if (e.target === sensorModal) {
                sensorModal.classList.add('hidden');
                sensorModal.classList.remove('flex');
            }
        });
    }
});