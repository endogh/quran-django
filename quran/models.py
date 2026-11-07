from django.db import models


class Surah(models.Model):
    number = models.IntegerField(primary_key=True)
    name_translit_id = models.CharField(max_length=100)
    name_translation_id = models.CharField(max_length=100)
    name_arab_short = models.CharField(max_length=50)
    revelation = models.CharField(max_length=20)
    number_of_verses = models.IntegerField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.number}. {self.name_translit_id}"


class Verse(models.Model):
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='verses')
    number_in_surah = models.IntegerField()
    text_arab = models.TextField()
    translit_en = models.TextField()
    translation_id = models.TextField()

    class Meta:
        ordering = ['number_in_surah']
        unique_together = [['surah', 'number_in_surah']]

    def __str__(self):
        return f"{self.surah.number}:{self.number_in_surah}"


class IPGeoCache(models.Model):
    """Cache hasil lookup IP -> negara agar API tidak dipanggil berulang."""

    ip = models.CharField(max_length=45, unique=True)
    country_code = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    resolved_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cache Geo IP'
        verbose_name_plural = 'Cache Geo IP'

    def __str__(self):
        return f"{self.ip} -> {self.country_name or 'Tidak diketahui'}"


class AccessLog(models.Model):
    """Catatan setiap kunjungan halaman (untuk statistik visitor)."""

    ip = models.CharField(max_length=45, db_index=True)
    country_code = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    path = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log Akses'
        verbose_name_plural = 'Log Akses'
        indexes = [
            models.Index(fields=['country_code']),
        ]

    def __str__(self):
        return f"{self.ip} {self.path} {self.created_at:%Y-%m-%d %H:%M}"

