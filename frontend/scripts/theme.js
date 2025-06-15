// theme.js
export function initTheme(targetId) {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.add(savedTheme);

    // Inject global styles: Chỉ áp dụng theme cho nội dung chính
    const style = document.createElement('style');
    style.textContent = `
        body.light {
            color: #000 !important;
            background-color: #ffffff !important;
        }

        body.dark {
            color: #fff !important;
            background-color: #000000 !important;
        }

        /* Chỉ áp dụng cho nội dung chính, KHÔNG ảnh hưởng sidebar, button */
        body.light main, body.light section, body.light article {
            background-color: #ffffff !important;
            color: #000 !important;
        }

        body.dark main, body.dark section, body.dark article {
            background-color: #000000 !important;
            color: #fff !important;
        }
    `;
    document.head.appendChild(style);

    // Nút chuyển đổi theme
    const toggleButton = document.createElement('button');
    toggleButton.innerHTML = savedTheme === 'light' 
      ? '🌞 Light Mode' 
      : '🌙 Dark Mode';

    // Style của nút
    toggleButton.style.position = 'relative';
    toggleButton.style.zIndex = '1000';
    toggleButton.style.padding = '10px 20px';
    toggleButton.style.border = 'none';
    toggleButton.style.borderRadius = '5px';
    toggleButton.style.cursor = 'pointer';
    toggleButton.style.fontSize = '16px';
    toggleButton.style.transition = 'background-color 0.3s, color 0.3s';
    toggleButton.style.backgroundColor = savedTheme === 'light' ? '#f0f0f0' : '#333';
    toggleButton.style.color = savedTheme === 'light' ? '#000' : '#fff';

    const targetElement = document.getElementById(targetId);
    if (targetElement) {
        targetElement.appendChild(toggleButton);
    } else {
        console.error(`Element with id "${targetId}" not found.`);
        return;
    }

    // Bắt sự kiện chuyển theme
    toggleButton.addEventListener('click', () => {
        const currentTheme = document.body.classList.contains('light') ? 'light' : 'dark';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.body.classList.remove(currentTheme);
        document.body.classList.add(newTheme);

        localStorage.setItem('theme', newTheme);

        toggleButton.innerHTML = newTheme === 'light' 
          ? '🌞 Light Mode' 
          : '🌙 Dark Mode';
        toggleButton.style.backgroundColor = newTheme === 'light' ? '#f0f0f0' : '#333';
        toggleButton.style.color = newTheme === 'light' ? '#000' : '#fff';
    });
}
