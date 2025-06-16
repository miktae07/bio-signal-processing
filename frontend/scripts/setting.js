// scripts/setting.js
import { toggleTheme, getTheme } from './theme.js';
import { setBackendAddress } from './backend_config.js';

document.addEventListener('DOMContentLoaded', () => {
  const themeBtn          = document.getElementById('change-theme-btn');
  const settingsDropdown  = document.getElementById('settings-dropdown');
  const settingsBtn       = document.getElementById('settings-btn');
  const connectBtn        = document.getElementById('connect-backend-btn');
  const backendModal      = document.getElementById('backend-modal');
  const cancelBtn         = document.getElementById('cancel-backend-btn');
  const submitBtn         = document.getElementById('submit-backend-btn');
  const addressInput      = document.getElementById('backend-address');

  // 1) Khởi label ngay khi load
  function updateThemeLabel() {
    const theme = getTheme(); // 'light' hoặc 'dark'
    themeBtn.textContent = theme === 'light'
      ? 'Dark Mode'      // đang sáng, gợi bấm để chuyển Dark
      : 'Light Mode';    // đang tối, gợi bấm để chuyển Light
  }
  updateThemeLabel();

  // 2) Click vào “Giao Diện”
  themeBtn.addEventListener('click', () => {
    const newTheme = toggleTheme();    // đổi và lấy về giá trị mới
    updateThemeLabel();                // cập nhật chữ cho nút
    settingsDropdown.classList.add('hidden');
  });

  // rest như cũ: toggle dropdown + xoay icon
  settingsBtn.addEventListener('click', () => {
    settingsDropdown.classList.toggle('hidden');
    settingsBtn.classList.add('rotate-anticlockwise');
    setTimeout(() => settingsBtn.classList.remove('rotate-anticlockwise'), 300);
  });

  // Connect Backend...
  connectBtn.addEventListener('click', () => {
    settingsDropdown.classList.add('hidden');
    backendModal.classList.toggle('hidden');
    backendModal.classList.toggle('flex');
  });
  cancelBtn.addEventListener('click', () => {
    backendModal.classList.add('hidden');
    backendModal.classList.remove('flex');
  });
  submitBtn.addEventListener('click', () => {
    const address = addressInput.value.trim();
    if (address) setBackendAddress(address);
    backendModal.classList.add('hidden');
    backendModal.classList.remove('flex');
  });
  backendModal.addEventListener('click', e => {
    if (e.target === backendModal) {
      backendModal.classList.add('hidden');
      backendModal.classList.remove('flex');
    }
  });
});
