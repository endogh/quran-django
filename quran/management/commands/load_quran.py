import json
from pathlib import Path
from django.core.management.base import BaseCommand
from quran.models import Surah, Verse


class Command(BaseCommand):
    help = 'Load Quran data from JSON'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[4]
        json_path = base_dir.parent / 'quran' / 'data' / 'quran.json'
        if not json_path.exists():
            json_path = Path('/home/mrx/Projects/PHP/quran/data/quran.json')
        
        self.stdout.write(f'Loading from {json_path}')
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        
        surahs_data = data.get('data', []) if isinstance(data, dict) else data
        Verse.objects.all().delete()
        Surah.objects.all().delete()
        
        for s in surahs_data:
            surah = Surah.objects.create(
                number=s['number'],
                name_translit_id=s['name']['transliteration']['id'],
                name_translation_id=s['name']['translation']['id'],
                name_arab_short=s['name']['short'],
                revelation=s['revelation'].get('id', ''),
                number_of_verses=s['numberOfVerses'],
            )
            for v in s.get('verses', []):
                Verse.objects.create(
                    surah=surah,
                    number_in_surah=v['number']['inSurah'],
                    text_arab=v['text']['arab'],
                    translit_en=v['text']['transliteration']['en'],
                    translation_id=v['translation']['id'],
                )
        self.stdout.write(self.style.SUCCESS(f'Loaded {Surah.objects.count()} surahs'))
