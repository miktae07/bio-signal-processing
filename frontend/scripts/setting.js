// scripts/setting.js
import { toggleTheme, getTheme } from './theme.js';
import { setBackendAddress } from './backend_config.js';

document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('change-theme-btn');
    const settingsDropdown = document.getElementById('settings-dropdown');
    const settingsBtn = document.getElementById('settings-btn');
    const connectBtn = document.getElementById('connect-backend-btn');
    const backendModal = document.getElementById('backend-modal');
    const cancelBtn = document.getElementById('cancel-backend-btn');
    const submitBtn = document.getElementById('submit-backend-btn');
    const addressInput = document.getElementById('backend-address');
    const languageSelect = document.getElementById('language-select');

    // Language data
    const languageData = {
        vi: {
            themeLabelLight: "Dark Mode",
            themeLabelDark: "Light Mode",
            connectBackend: "Kết Nối Backend",
            languageLabel: "Ngôn Ngữ",
            currentLanguage: "Tiếng Việt",
        },
        en: {
            themeLabelLight: "Dark Mode",
            themeLabelDark: "Light Mode",
            connectBackend: "Connect Backend",
            languageLabel: "Language",
            currentLanguage: "English",
        },
    };

    // Function to update language
    function updateLanguage(lang) {
        const data = languageData[lang] || languageData.vi; // Default to Vietnamese
        themeBtn.textContent = getTheme() === 'light'
            ? data.themeLabelLight
            : data.themeLabelDark;
        connectBtn.textContent = data.connectBackend;
        document.querySelector('label[for="language-select"]').textContent = data.languageLabel;
    }

    // Initialize language on page load
    const savedLang = localStorage.getItem('language') || 'vi'; // Default to Vietnamese
    languageSelect.value = savedLang;
    updateLanguage(savedLang);

    // Event listener for language selection
    languageSelect.addEventListener('change', (event) => {
        const selectedLang = event.target.value;
        localStorage.setItem('language', selectedLang); // Save language preference
        updateLanguage(selectedLang);
    });

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

    // Close backend modal when clicking outside the modal content
    backendModal.addEventListener('click', (e) => {
        if (e.target === backendModal) {
            backendModal.classList.add('hidden');
            backendModal.classList.remove('flex');
        }
    });
});
