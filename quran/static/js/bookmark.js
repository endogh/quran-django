(function() {
    var verseCards = document.querySelectorAll("[data-ayah].rounded-2xl");
    var bookmarkBtns = document.querySelectorAll(".bookmark-ayah");

    if (!verseCards.length && !bookmarkBtns.length) return;

    function setBookmark(surah, ayah) {
        try {
            localStorage.setItem("lastSurah", String(surah));
            localStorage.setItem("lastAyah", String(ayah));
        } catch(e) {}
    }

    function flashIcon(icon) {
        if (!icon) return;
        icon.className = 'bi bi-bookmark-fill text-emerald-500 text-lg';
        setTimeout(function() {
            icon.className = 'bi bi-bookmark-plus text-lg';
        }, 2000);
    }

    function showToast(surah, ayah) {
        var old = document.getElementById('bookmarkToast');
        if (old) old.remove();
        var toast = document.createElement('div');
        toast.id = 'bookmarkToast';
        toast.className = 'fixed bottom-20 right-6 z-50 bg-emerald-500 text-white px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all duration-300';
        toast.innerHTML = '<i class="bi bi-bookmark-fill me-1"></i> Bookmark disimpan! Surah ' + surah + ', Ayat ' + ayah;
        document.body.appendChild(toast);
        setTimeout(function() {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(function() { toast.remove(); }, 300);
        }, 2500);
    }

    bookmarkBtns.forEach(function(btn) {
        btn.addEventListener("click", function(e) {
            e.stopPropagation();
            e.preventDefault();
            var surah = this.getAttribute("data-surah");
            var ayah = this.getAttribute("data-ayah");
            if (surah && ayah) {
                setBookmark(surah, ayah);
                flashIcon(this.querySelector('i'));
                showToast(surah, ayah);
                try { document.dispatchEvent(new Event('bookmarkUpdated')); } catch(e) {}
            }
        });
    });

    verseCards.forEach(function(card) {
        card.addEventListener("click", function(e) {
            if (e.target.closest('.bookmark-ayah')) return;
            var surah = this.getAttribute("data-surah");
            var ayah = this.getAttribute("data-ayah");
            if (surah && ayah) {
                setBookmark(surah, ayah);
                flashIcon(this.querySelector('.bookmark-ayah i'));
                showToast(surah, ayah);
                try { document.dispatchEvent(new Event('bookmarkUpdated')); } catch(e) {}
            }
        });
    });

    function highlightAyah(ayahNum) {
        if (!ayahNum) return;
        var cards = document.querySelectorAll("[data-ayah].rounded-2xl");
        for (var i = 0; i < cards.length; i++) {
            if (cards[i].getAttribute("data-ayah") === ayahNum) {
                (function(card) {
                    setTimeout(function() {
                        card.scrollIntoView({ behavior: "smooth", block: "center" });
                        card.classList.add("ring-2", "ring-emerald-400", "shadow-lg");
                        setTimeout(function() {
                            card.classList.remove("ring-2", "ring-emerald-400", "shadow-lg");
                        }, 4000);
                    }, 600);
                })(cards[i]);
                break;
            }
        }
    }

    var lastAyah = null;
    try { lastAyah = localStorage.getItem("lastAyah"); } catch(e) {}
    highlightAyah(lastAyah);

    var urlParams = new URLSearchParams(window.location.search);
    var ayahParam = urlParams.get("ayah");
    if (ayahParam && ayahParam !== lastAyah) {
        highlightAyah(ayahParam);
    }
})();
