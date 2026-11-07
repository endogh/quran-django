# Quran Kareem — Quran Online Django

Aplikasi web Al-Qur'an online berbahasa Indonesia: 114 surah lengkap dengan teks Arab, transliterasi, dan terjemahan. Dilengkapi dashboard statistik visitor, SEO, dan optimasi untuk mesin pencari berbasis AI (GEO).

Live: <https://quran.codenest.id>

## Fitur

- **114 surah & seluruh ayat** — teks Arab, transliterasi, terjemahan Indonesia, penanda Makkiyah/Madaniyah.
- **Pencarian & navigasi surah** — daftar surah di beranda, halaman detail per surah, tombol surah sebelumnya/berikutnya.
- **Mode gelap** — preferensi tersimpan di browser.
- **Dashboard statistik visitor** (rahasia):
  - total visitor unik & page view, visitor/page view hari ini;
  - grafik kunjungan 30 hari terakhir;
  - jam paling ramai (WIB);
  - negara teratas + tabel rincian (deteksi via IP, di-cache);
  - halaman paling sering dibuka.
- **Auto-retensi log** — log lebih lama dari `STATS_RETENTION_DAYS` dihapus otomatis, plus perintah manual `purge_access_logs`.
- **Filter bot** — crawler/Googlebot/curl tidak dihitung sebagai visitor.
- **SEO** — title & description dinamis, canonical, hreflang, Open Graph, Twitter Card, JSON-LD (`WebSite`, `Chapter`, `BreadcrumbList`), `robots.txt`, `sitemap.xml`.
- **GEO (Generative Engine Optimization)** — `llms.txt` + izin crawler AI (`GPTBot`, `ClaudeBot`, `PerplexityBot`, dll.) di `robots.txt`.

## Teknologi

- Python 3 · Django 6.1
- SQLite
- Gunicorn
- Tailwind CSS (CDN) · Bootstrap Icons · Chart.js
- `requests` untuk lookup geo IP (ip-api.com)
- `python-dotenv` untuk konfigurasi `.env`

## Struktur Proyek

```
quran-django/
├── core/                    # konfigurasi project (settings, urls, wsgi)
├── quran/
│   ├── middleware.py        # pencatat kunjungan (AccessLog)
│   ├── models.py            # Surah, Verse, AccessLog, IPGeoCache
│   ├── views.py             # halaman + stats + robots/sitemap/llms
│   ├── urls.py
│   ├── management/commands/
│   │   └── purge_access_logs.py
│   ├── static/              # css, js, font, gambar
│   └── templates/quran/     # index, surah, credit, stats, sitemap.xml
├── deploy.sh                # deploy otomatis dari GitHub
├── requirements.txt
├── .env.example
└── manage.py
```

## Prasyarat

- Python 3.10+ (disarankan 3.12+)
- Git

## Instalasi Lokal

```bash
git clone https://github.com/endogh/quran-django.git
cd quran-django

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# edit .env sesuai kebutuhan

python manage.py migrate
python manage.py runserver
```

Buka <http://127.0.0.1:8000/>.

> Data surah/ayat diambil dari [github.com/gadingnst/quran-api](https://github.com/gadingnst/quran-api). Jika database belum berisi data, impor terlebih dahulu sebelum aplikasi digunakan.

## Konfigurasi `.env`

Salin `.env.example` menjadi `.env` (file `.env` **tidak** ikut ter-commit).

```env
# Token rahasia untuk membuka dashboard statistik.
STATS_SECRET_KEY=ganti-dengan-token-acak

# Path URL rahasia dashboard (tanpa slash di awal/akhir).
STATS_URL=stats-rahasia

# Simpan log kunjungan selama N hari (dibersihkan otomatis).
STATS_RETENTION_DAYS=90

# Origin yang diizinkan untuk login/POST (CSRF). Pisahkan dengan koma.
CSRF_TRUSTED_ORIGINS=https://domainmu.com,http://domainmu.com
```

### Mengakses dashboard statistik

1. Login sebagai superuser/staff di `/admin/`.
2. Buka `https://domainmu.com/<STATS_URL>/?key=<STATS_SECRET_KEY>`.

Tanpa login staff atau dengan token salah, halaman akan menghasilkan 404 (disembunyikan).

## Perintah Berguna

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py purge_access_logs            # hapus log > STATS_RETENTION_DAYS
python manage.py purge_access_logs --days 30  # override retensi
python manage.py createsuperuser
```

## Deploy ke Server

Repo ini menyertakan `deploy.sh` untuk deploy otomatis dari GitHub:

```bash
cd /opt/quran
./deploy.sh
```

Yang dilakukan script:

1. `git fetch` + `git reset --hard origin/main` (perubahan lokal di-auto-stash).
2. Deteksi virtualenv otomatis (`.venv`, `venv`, `.Quranvenv`, `../.venv`, `/opt/venv`).
3. `pip install -r requirements.txt`.
4. Backup `db.sqlite3` ke `backups/` (menyimpan 10 backup terbaru).
5. `migrate`, `collectstatic`, dan `purge_access_logs`.
6. Restart aplikasi via **PM2** (`pm2 restart quran-django`) atau **systemd**, jika tidak ada akan menampilkan perintah manual.

Opsi environment:

```bash
BRANCH=main ./deploy.sh
VENV_DIR=/path/venv ./deploy.sh
PM2_APP=quran-django ./deploy.sh
SKIP_BACKUP=1 ./deploy.sh
```

### Contoh konfigurasi nginx

```nginx
location /static/ { alias /opt/quran/staticfiles/; }
location / {
    proxy_pass http://127.0.0.1:7000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Cron pembersihan log (opsional)

```cron
0 3 * * * cd /opt/quran && /path/venv/bin/python manage.py purge_access_logs
```

## Endpoint Penting

| URL | Keterangan |
|-----|------------|
| `/` | Beranda & daftar surah |
| `/surah/<nomor>/` | Detail surah |
| `/credit` | Sumber data & kredit |
| `/admin/` | Admin Django |
| `/robots.txt` | Aturan crawler |
| `/sitemap.xml` | Sitemap dinamis |
| `/llms.txt` | Ringkasan situs untuk crawler AI |
| `/<STATS_URL>/?key=...` | Dashboard statistik (staff + token) |

## Kredit

- Data Al-Qur'an: [gadingnst/quran-api](https://github.com/gadingnst/quran-api)
- Font Arab: Amiri, Scheherazade New, Lateef, Noto Naskh Arabic
- Dibuat oleh [Codenest](https://codenest.id)
