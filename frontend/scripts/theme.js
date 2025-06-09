// theme.js
export function initTheme(targetId) {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.add(savedTheme);

    // Dynamically inject global styles for text color
    const style = document.createElement('style');
    style.textContent = `
        body.light, body.light * {
            color: #000 !important; /* Text color for light mode */
            background-color: #ffffff !important; /* Background color for light mode */
        }
        body.dark, body.dark * {
            color: #fff !important; /* Text color for dark mode */
            background-color: #000000 !important; /* Background color for dark mode */
        }
    `;
    document.head.appendChild(style);

    const toggleButton = document.createElement('button');
    toggleButton.innerHTML = savedTheme === 'light' 
      ? '🌞 Light Mode' 
      : '🌙 Dark Mode';
    toggleButton.style.position = 'relative'; // Adjust position for appending to a specific element
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

        // Update body class
        document.body.classList.remove(currentTheme);
        document.body.classList.add(newTheme);

        // Save theme to localStorage
        localStorage.setItem('theme', newTheme);

        // Update button styles and text dynamically
        toggleButton.innerHTML = newTheme === 'light' 
          ? '🌞 Light Mode' 
          : '🌙 Dark Mode';
        toggleButton.style.backgroundColor = newTheme === 'light' ? '#f0f0f0' : '#333';
        toggleButton.style.color = newTheme === 'light' ? '#000' : '#fff';
    });
}