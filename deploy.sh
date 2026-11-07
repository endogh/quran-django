#!/usr/bin/env bash
#
# deploy.sh — deploy otomatis quran-django dari GitHub.
#
# Cara pakai di server:
#   cd /opt/quran        # folder project (berisi file ini)
#   ./deploy.sh
#
# Opsi lewat environment variable (opsional):
#   BRANCH=main ./deploy.sh          # branch yang di-pull
#   VENV_DIR=/path/venv ./deploy.sh  # paksa lokasi virtualenv
#   PM2_APP=quran-django ./deploy.sh # nama app PM2
#   SKIP_BACKUP=1 ./deploy.sh        # lewati backup SQLite
#
set -euo pipefail

APP_NAME="quran-django"
REPO_URL="https://github.com/endogh/quran-django.git"
BRANCH="${BRANCH:-main}"
PM2_APP="${PM2_APP:-$APP_NAME}"
SYSTEMD_SERVICE="${SYSTEMD_SERVICE:-$APP_NAME}"

# Lokasi folder project = folder tempat deploy.sh berada.
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
cd "$PROJECT_DIR"

# ---------- helper ----------
c_reset='\033[0m'; c_blue='\033[0;34m'; c_green='\033[0;32m'
c_yellow='\033[0;33m'; c_red='\033[0;31m'
info()  { echo -e "${c_blue}[deploy]${c_reset} $*"; }
ok()    { echo -e "${c_green}[ok]${c_reset} $*"; }
warn()  { echo -e "${c_yellow}[warn]${c_reset} $*"; }
fail()  { echo -e "${c_red}[error]${c_reset} $*" >&2; exit 1; }

# ---------- 0. cek git ----------
command -v git >/dev/null 2>&1 || fail "git tidak ditemukan."
if [ ! -d .git ]; then
  info "Folder ini belum berupa repo git. Clone dari GitHub..."
  [ -n "$(ls -A . 2>/dev/null | grep -v '^deploy.sh$' || true)" ] \
    && fail "Folder tidak kosong. Kosongkan dulu atau clone manual: git clone $REPO_URL ."
  git init -q
  git remote add origin "$REPO_URL"
  git fetch origin "$BRANCH"
  git checkout -B "$BRANCH" "origin/$BRANCH"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$REPO_URL"
fi

# ---------- 1. pull kode terbaru ----------
info "Mengambil kode terbaru dari origin/$BRANCH ..."
git fetch origin "$BRANCH"
# Simpan perubahan lokal yang tidak ter-commit (kalau ada) agar tidak hilang.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  STASH_NAME="deploy-autostash-$(date +%Y%m%d-%H%M%S)"
  warn "Ada perubahan lokal. Disimpan sementara ke stash: $STASH_NAME"
  git stash push -u -m "$STASH_NAME" >/dev/null
fi
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
ok "Kode diperbarui ke $(git rev-parse --short HEAD) — $(git log -1 --pretty=%s)"

# ---------- 2. deteksi virtualenv ----------
find_python() {
  local candidates=()
  [ -n "${VENV_DIR:-}" ] && candidates+=("$VENV_DIR")
  candidates+=(
    "$PROJECT_DIR/.venv"
    "$PROJECT_DIR/venv"
    "$PROJECT_DIR/.Quranvenv"
    "$PROJECT_DIR/../.venv"
    "/opt/venv"
  )
  for dir in "${candidates[@]}"; do
    if [ -x "$dir/bin/python" ]; then
      echo "$dir/bin/python"
      return 0
    fi
  done
  command -v python3 || true
}

PYTHON_BIN="$(find_python)"
[ -n "$PYTHON_BIN" ] || fail "Python tidak ditemukan. Set VENV_DIR=/path/venv."
info "Python: $PYTHON_BIN"

# ---------- 3. install dependency ----------
if [ -f requirements.txt ]; then
  info "Install dependency (pip) ..."
  "$PYTHON_BIN" -m pip install --upgrade pip >/dev/null 2>&1 || true
  "$PYTHON_BIN" -m pip install -r requirements.txt
  ok "Dependency terpasang."
else
  warn "requirements.txt tidak ada, lewati pip install."
fi

# ---------- 4. backup database SQLite ----------
DB_FILE="$PROJECT_DIR/db.sqlite3"
if [ -f "$DB_FILE" ] && [ "${SKIP_BACKUP:-0}" != "1" ]; then
  BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
  mkdir -p "$BACKUP_DIR"
  BACKUP_FILE="$BACKUP_DIR/db-$(date +%Y%m%d-%H%M%S).sqlite3"
  cp "$DB_FILE" "$BACKUP_FILE"
  ok "Backup database: $BACKUP_FILE"
  # Simpan hanya 10 backup terbaru.
  ls -1t "$BACKUP_DIR"/db-*.sqlite3 2>/dev/null | tail -n +11 | xargs -r rm -f
fi

# ---------- 5. migrate & collectstatic ----------
if [ -f manage.py ]; then
  info "Menjalankan migrasi database ..."
  "$PYTHON_BIN" manage.py migrate --noinput
  ok "Migrasi selesai."

  info "Mengumpulkan file statis ..."
  "$PYTHON_BIN" manage.py collectstatic --noinput >/dev/null
  ok "Static files siap."

  # Bersihkan log kunjungan lama (kalau command tersedia).
  "$PYTHON_BIN" manage.py purge_access_logs >/dev/null 2>&1 || true
else
  warn "manage.py tidak ditemukan, lewati migrate/collectstatic."
fi

# ---------- 6. restart aplikasi ----------
restarted=0
if command -v pm2 >/dev/null 2>&1; then
  if pm2 describe "$PM2_APP" >/dev/null 2>&1; then
    info "Restart PM2: $PM2_APP ..."
    pm2 restart "$PM2_APP" --update-env
    restarted=1
  elif [ -n "${PM2_ECOSYSTEM:-}" ] && [ -f "${PM2_ECOSYSTEM}" ]; then
    info "Start PM2 dari ecosystem: $PM2_ECOSYSTEM ..."
    pm2 start "$PM2_ECOSYSTEM" --only "$PM2_APP" --update-env
    restarted=1
  fi
fi

if [ "$restarted" -eq 0 ] && command -v systemctl >/dev/null 2>&1; then
  if systemctl list-unit-files 2>/dev/null | grep -q "^${SYSTEMD_SERVICE}\.service"; then
    info "Restart systemd: $SYSTEMD_SERVICE ..."
    sudo systemctl restart "$SYSTEMD_SERVICE"
    restarted=1
  fi
fi

if [ "$restarted" -eq 1 ]; then
  ok "Aplikasi berhasil di-restart."
else
  warn "PM2/systemd tidak terdeteksi. Restart manual, contoh:"
  echo "    pm2 restart $PM2_APP"
  echo "    # atau"
  echo "    sudo systemctl restart $SYSTEMD_SERVICE"
fi

echo
ok "Deploy $APP_NAME selesai! (commit $(git rev-parse --short HEAD))"
