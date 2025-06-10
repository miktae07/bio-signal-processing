// theme.js
export function initTheme(targetId) {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.add(savedTheme);

    // Inject global styles, KHÔNG ép màu sidebar nữa
    const style = document.createElement('style');
    style.textContent = `
        body.light, body.light *:not(#sidebar):not(#sidebar *) {
            color: #000 !important;
            background-color: #ffffff !important;
        }
        body.dark, body.dark *:not(#sidebar):not(#sidebar *) {
            color: #fff !important;
            background-color: #000000 !important;
        }
        /* KHÔNG ép màu sidebar ở đây, để CSS quyết định */
    `;
    document.head.appendChild(style);

    const toggleButton = document.createElement('button');
    toggleButton.innerHTML = savedTheme === 'light' 
      ? '🌞 Light Mode' 
      : '🌙 Dark Mode';
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