from django.shortcuts import render, get_object_or_404
from .models import Surah


def index(request):
    surahs = Surah.objects.all().prefetch_related('verses')
    total_surahs = surahs.count()
    total_verses = sum(s.number_of_verses for s in surahs)
    return render(request, 'quran/index.html', {
        'surahs': surahs,
        'total_surahs': total_surahs,
        'total_verses': total_verses,
    })


def surah_detail(request, surah_number):
    surahs = Surah.objects.all().prefetch_related('verses')
    surah_data = get_object_or_404(Surah.objects.prefetch_related('verses'), number=surah_number)
    prev_surah = surah_number - 1 if surah_number > 1 else None
    next_surah = surah_number + 1 if surah_number < 114 else None
    all_surahs = list(surahs)
    return render(request, 'quran/surah.html', {
        'surah_data': surah_data,
        'surahs': all_surahs,
        'prev_surah': prev_surah,
        'next_surah': next_surah,
    })


def surah_php(request):
    surah_number = request.GET.get('surah')
    if surah_number:
        try:
            return surah_detail(request, int(surah_number))
        except Exception:
            pass
    return index(request)


def credit(request):
    return render(request, 'quran/credit.html')
