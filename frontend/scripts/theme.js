// scripts/theme.js

let currentTheme;

export function initTheme() {
  currentTheme = localStorage.getItem('theme') || 'light';
  document.body.classList.add(currentTheme);
}

export function toggleTheme() {
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.body.classList.replace(currentTheme, newTheme);
  currentTheme = newTheme;
  localStorage.setItem('theme', newTheme);
  return newTheme;           // <— trả về để biết ta vừa chuyển sang gì
}

export function getTheme() {
  return currentTheme;
}
