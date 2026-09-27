const THEME_STORAGE_KEY = 'internworld-theme';

function getSavedTheme() {
    return localStorage.getItem(THEME_STORAGE_KEY) || 'light';
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    updateThemeToggleButton(theme);
    
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
}

function toggleTheme() {
    const currentTheme = getSavedTheme();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function updateThemeToggleButton(theme) {
    const toggleBtn = document.getElementById('themeToggle');
    if (!toggleBtn) return;
    
    if (theme === 'dark') {
        toggleBtn.innerHTML = '<i class="bi bi-moon-stars-fill text-warning"></i>';
    } else {
        toggleBtn.innerHTML = '<i class="bi bi-sun-fill text-warning"></i>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateThemeToggleButton(getSavedTheme());
});

window.toggleTheme = toggleTheme;
