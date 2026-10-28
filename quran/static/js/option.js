(function() {
    var fontSelector = document.getElementById('fontSelector');
    var fontDecrease = document.getElementById('fontDecrease');
    var fontIncrease = document.getElementById('fontIncrease');
    var fontSizeDisplay = document.getElementById('fontSizeDisplay');
    var bookmarkBtn = document.getElementById('bookmarkBtn');
    var loadBookmarkBtn = document.getElementById('load-bookmark-btn');

    var arabicTexts = document.querySelectorAll('.font-arabic');
    if (!arabicTexts.length) return;

    var FONT_MAP = {
        'Amiri': 'Amiri, serif',
        'Scheherazade New': '"Scheherazade New", serif',
        'Lateef': 'Lateef, serif',
        'Noto Naskh Arabic': '"Noto Naskh Arabic", serif',
        'Reem Kufi': '"Reem Kufi", sans-serif',
        'Traditional Arabic': '"Traditional Arabic", serif',
        'Me Quran': '"Me Quran", serif',
    };

    var FONT_LABELS = ['1', '1.5', '2', '2.5', '3', '3.5', '4'];
    var FONT_LABEL_NAMES = {
        '1': 'Kecil', '1.5': 'Sedang', '2': 'Medium',
        '2.5': 'Besar', '3': 'XL', '3.5': 'XXL', '4': 'XXXL'
    };

    var currentSize = localStorage.getItem('arabicFontSize') || '2.5';
    var currentFont = localStorage.getItem('arabicFont') || 'Amiri';

    if (!FONT_LABELS.includes(currentSize)) currentSize = '2.5';
    if (!FONT_MAP[currentFont]) currentFont = 'Amiri';

    function applyFontSize(size) {
        for (var i = 0; i < arabicTexts.length; i++) {
            arabicTexts[i].style.fontSize = size + 'rem';
        }
        try { localStorage.setItem('arabicFontSize', size); } catch(e) {}
        if (fontSizeDisplay) fontSizeDisplay.textContent = FONT_LABEL_NAMES[size] || size + 'rem';
    }

    function applyFont(font) {
        var family = FONT_MAP[font] || 'Amiri, serif';
        for (var i = 0; i < arabicTexts.length; i++) {
            arabicTexts[i].style.fontFamily = family;
        }
        try { localStorage.setItem('arabicFont', font); } catch(e) {}
    }

    applyFontSize(currentSize);
    applyFont(currentFont);

    if (fontSelector) {
        fontSelector.value = currentFont;
        fontSelector.addEventListener('change', function() {
            applyFont(this.value);
        });
    }

    if (fontDecrease) {
        fontDecrease.addEventListener('click', function() {
            var idx = FONT_LABELS.indexOf(currentSize);
            if (idx > 0) {
                currentSize = FONT_LABELS[idx - 1];
                applyFontSize(currentSize);
            }
        });
    }

    if (fontIncrease) {
        fontIncrease.addEventListener('click', function() {
            var idx = FONT_LABELS.indexOf(currentSize);
            if (idx < FONT_LABELS.length - 1) {
                currentSize = FONT_LABELS[idx + 1];
                applyFontSize(currentSize);
            }
        });
    }

    function goToBookmark() {
        var surah = null, ayah = null;
        try {
            surah = localStorage.getItem('lastSurah');
            ayah = localStorage.getItem('lastAyah');
        } catch(e) {}
        if (surah && ayah) {
            window.location.href = '/surah/' + encodeURIComponent(surah) + '/?ayah=' + encodeURIComponent(ayah);
        } else if (surah) {
            window.location.href = '/surah/' + encodeURIComponent(surah) + '/';
        } else {
            alert('Belum ada bookmark yang tersimpan!');
        }
    }

    if (bookmarkBtn) bookmarkBtn.addEventListener('click', goToBookmark);
    if (loadBookmarkBtn) loadBookmarkBtn.addEventListener('click', goToBookmark);
})();
