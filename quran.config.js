module.exports = {
  apps: [
    {
      name: "django-app",
      // Menggunakan interpreter Python langsung untuk mengeksekusi modul gunicorn
      script: "/opt/Quran/.Quranvenv/bin/gunicorn",
      // Penambahan argumen yang tepat untuk eksekusi WSGI gunicorn
      args: " --bind 0.0.0.0:7000 core.wsgi:application",
      // MEMPERBAIKI PATH: Diubah ke /opt/Quran sesuai dengan lokasi asli project Anda
      cwd: "/opt/Quran", 
      interpreter: "/opt/Quran/.Quranvenv/bin/python3",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
