#!/bin/bash

# Pastikan skrip dijalankan sebagai root
if [ "$EUID" -ne 0 ]; then
  echo "[-] Skrip ini harus dijalankan sebagai root (gunakan sudo)."
  exit 1
fi

OLD_PYENV="/root/.pyenv"
NEW_PYENV="/opt/.pyenv"

echo "[1/4] Memeriksa folder Pyenv asal..."
if [ ! -d "$OLD_PYENV" ]; then
  echo "[-] Error: Folder $OLD_PYENV tidak ditemukan!"
  exit 1
fi

echo "[2/4] Memindahkan Pyenv ke $NEW_PYENV..."
if [ -d "$NEW_PYENV" ]; then
  echo "[!] Folder $NEW_PYENV sudah ada. Membuat backup ke ${NEW_PYENV}_backup..."
  mv "$NEW_PYENV" "${NEW_PYENV}_backup"
fi
mv "$OLD_PYENV" "$NEW_PYENV"

echo "[3/4] Mengatur hak akses (Permission) agar bisa dibaca semua user..."
# Memberikan akses baca & eksekusi untuk semua user, tapi tulis hanya untuk root
chown -R root:root "$NEW_PYENV"
chmod -R 755 "$NEW_PYENV"

echo "[4/4] Memperbaiki internal path Pyenv..."
# Pyenv sering menyimpan hardcode path /root/.pyenv di file konfigurasinya
find "$NEW_PYENV" -type f -exec sed -i "s|/root/.pyenv|/opt/.pyenv|g" {} + 2>/dev/null

echo "[+] Selesai! Pyenv berhasil dipindahkan ke $NEW_PYENV"
echo "[i] Silakan buat ulang venv Anda sekarang menggunakan Python dari path baru."
