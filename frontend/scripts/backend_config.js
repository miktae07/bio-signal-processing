// scripts/backend_config.js

let backendAddress = 'http://localhost:5000'; // Mặc định

export function setBackendAddress(address) {
    if (!address || typeof address !== 'string') {
        console.error('Địa chỉ backend không hợp lệ');
        return;
    }
    backendAddress = address;
    console.log(`Địa chỉ backend đã được cập nhật: ${backendAddress}`);
    localStorage.setItem('backendAddress', address); // Optional: Lưu vào localStorage
}

export function getBackendAddress() {
    console.log(`Địa chỉ backend hiện tại: ${backendAddress}`);
    return backendAddress;
}

// Optional: Load từ localStorage nếu có
const savedAddress = localStorage.getItem('backendAddress');
if (savedAddress) {
    console.log(`Địa chỉ backend được lưu trong localStorage: ${savedAddress}`);
    backendAddress = savedAddress;
}
