// Theme toggle functionality disabled - no theme settings panel

document.addEventListener("DOMContentLoaded", function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const lightModeToggle = document.getElementById('light-mode-toggle');
    const darkMode = localStorage.getItem('darkMode');

    function enableDarkMode() {  
        document.documentElement.setAttribute('data-theme', 'dark');
        if (darkModeToggle) darkModeToggle.classList.remove('activate');
        if (lightModeToggle) lightModeToggle.classList.add('activate');
        localStorage.setItem('darkMode', 'enabled');
    }

    function disableDarkMode() {
        document.documentElement.setAttribute('data-theme', 'light');
        if (lightModeToggle) lightModeToggle.classList.remove('activate');
        if (darkModeToggle) darkModeToggle.classList.add('activate');
        localStorage.removeItem('darkMode');
    }

    // Check if darkModeToggle and lightModeToggle exist before adding event listeners
    if (darkModeToggle && lightModeToggle) {
        // Check the current mode on page load
        if (darkMode === 'enabled') {
            enableDarkMode();
        } else {
            disableDarkMode();
        }

        // Add event listeners
        darkModeToggle.addEventListener('click', enableDarkMode);
        lightModeToggle.addEventListener('click', disableDarkMode);
    }

    // Apply saved theme preferences without showing theme panel
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedSidebarTheme = localStorage.getItem('sidebarTheme') || 'light';
    const savedColor = localStorage.getItem('color') || 'primary';
    const savedLayout = localStorage.getItem('layout') || 'default';
    const savedTopbar = localStorage.getItem('topbar') || 'white';
    const savedWidth = localStorage.getItem('width') || 'fluid';
    const savedSidebarBg = localStorage.getItem('sidebarBg') || null;
    const savedTopbarBg = localStorage.getItem('topbarbg') || null;

    // Apply theme settings
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.documentElement.setAttribute('data-sidebar', savedSidebarTheme);
    document.documentElement.setAttribute('data-color', savedColor);
    document.documentElement.setAttribute('data-layout', savedLayout);
    document.documentElement.setAttribute('data-topbar', savedTopbar);
    document.documentElement.setAttribute('data-width', savedWidth);

    if (savedSidebarBg) {
        document.body.setAttribute('data-sidebarbg', savedSidebarBg);
    }

    if (savedTopbarBg) {
        document.body.setAttribute('data-topbarbg', savedTopbarBg);
    }

    // Handle layout classes
    if (savedLayout === 'mini') {
        document.body.classList.add("mini-sidebar");
        document.body.classList.remove("menu-horizontal");
    } else if (savedLayout === 'horizontal') {
        document.body.classList.add("menu-horizontal");
        document.body.classList.remove("mini-sidebar");
    } else if (savedLayout === 'horizontal-single') {
        document.body.classList.add("menu-horizontal");
        document.body.classList.remove("mini-sidebar");
    } else if (savedLayout === 'horizontal-overlay') {
        document.body.classList.add("menu-horizontal");
        document.body.classList.remove("mini-sidebar");
    } else {
        document.body.classList.remove("mini-sidebar", "menu-horizontal");
    }

    if (savedWidth === 'box') {
        document.body.classList.add("layout-box-mode");
    } else {
        document.body.classList.remove("layout-box-mode");
    }

    // Apply custom RGB colors if set
    const savedColorPickr = localStorage.getItem('primaryRGB');
    if (savedColorPickr) {
        let html = document.querySelector("html");
        html.style.setProperty("--primary-rgb", savedColorPickr);
    }

    const savedTopbarPickr = localStorage.getItem('topbarRGB');
    if (savedTopbarPickr) {
        let html = document.querySelector("html");
        html.style.setProperty("--topbar-rgb", savedTopbarPickr);
    }

    const savedSidebarPickr = localStorage.getItem('sidebarRGB');
    if (savedSidebarPickr) {
        let html = document.querySelector("html");
        html.style.setProperty("--sidebar-rgb", savedSidebarPickr);
    }
});
