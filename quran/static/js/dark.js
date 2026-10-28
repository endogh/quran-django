(function() {
    try {
        var savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
            document.documentElement.classList.add("dark");
        } else if (savedTheme === "light") {
            document.documentElement.classList.remove("dark");
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        }
    } catch(e) {}

    function applySwitchState() {
        var darkSwitch = document.getElementById('darkModeSwitch');
        if (!darkSwitch) return;
        var isDark = document.documentElement.classList.contains('dark');
        var thumb = darkSwitch.querySelector('span');
        if (isDark) {
            darkSwitch.style.backgroundColor = '#3b82f6';
            if (thumb) thumb.style.transform = 'translateX(20px)';
        } else {
            darkSwitch.style.backgroundColor = '#cbd5e1';
            if (thumb) thumb.style.transform = 'translateX(0)';
        }
    }

    var darkToggle = document.getElementById("darkToggle");
    if (darkToggle) {
        darkToggle.addEventListener("click", function() {
            document.documentElement.classList.toggle("dark");
            try { localStorage.setItem("theme", document.documentElement.classList.contains("dark") ? "dark" : "light"); } catch(e) {}
            applySwitchState();
            try { document.dispatchEvent(new Event('themeChanged')); } catch(e) {}
        });
    }

    var darkModeSwitch = document.getElementById("darkModeSwitch");
    if (darkModeSwitch) {
        applySwitchState();
        darkModeSwitch.addEventListener("click", function() {
            document.documentElement.classList.toggle("dark");
            try { localStorage.setItem("theme", document.documentElement.classList.contains("dark") ? "dark" : "light"); } catch(e) {}
            applySwitchState();
            try { document.dispatchEvent(new Event('themeChanged')); } catch(e) {}
        });
    }

    try { document.addEventListener('themeChanged', applySwitchState); } catch(e) {}
})();
