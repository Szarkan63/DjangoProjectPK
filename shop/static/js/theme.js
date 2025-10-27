(function () {
    const THEME_KEY = 'app.theme';
    const FONT_KEY = 'app.theme.font';


    const fontMap = {
        swit: "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
        zmierzch: "'Merriweather', Georgia, 'Times New Roman', serif",
        noc: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
    };

    function applyTheme(theme) {
        const root = document.documentElement;
        root.setAttribute('data-theme', theme);
        const font = fontMap[theme] || fontMap.swit;
        root.style.setProperty('--font-family', font);

        // Zachowaj wybory
        try {
            localStorage.setItem(THEME_KEY, theme);
            localStorage.setItem(FONT_KEY, font);
        } catch (_) { /* ignore */ }
    }

    function init() {
        const select = document.getElementById('theme-select');
        // Przywróć zapisany motyw
        let savedTheme = 'swit';
        try {
            savedTheme = localStorage.getItem(THEME_KEY) || savedTheme;
        } catch (_) { /* ignore */ }
        applyTheme(savedTheme);
        if (select) {
            select.value = savedTheme;
            select.addEventListener('change', (e) => {
                applyTheme(e.target.value);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();