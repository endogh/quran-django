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

