import json
from datetime import timedelta

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import ExtractHour, TruncDate
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone

from .models import AccessLog, Surah

SITE_NAME = 'Quran Kareem'
DEFAULT_DESCRIPTION = (
    "Baca Al-Qur'an online 30 juz lengkap 114 surah dengan teks Arab, "
    "transliterasi, dan terjemahan bahasa Indonesia. Gratis, cepat, dan "
    "nyaman di HP maupun desktop."
)
DEFAULT_KEYWORDS = (
    'quran online, al-quran, baca quran, terjemahan quran, '
    'quran 30 juz, surah, ayat'
)


def _seo(request, *, title, description=DEFAULT_DESCRIPTION, path=None,
         seo_type='website', robots='index, follow', keywords=None, json_ld=None):
    """Bangun context SEO standar untuk template head.html."""
    canonical = request.build_absolute_uri(path or request.path)
    return {
        'seo_title': title,
        'seo_description': description,
        'canonical_url': canonical,
        'seo_type': seo_type,
        'seo_robots': robots,
        'seo_keywords': keywords or DEFAULT_KEYWORDS,
        'seo_image': request.build_absolute_uri(static('images/logoquran.png')),
        'json_ld': json.dumps(json_ld, ensure_ascii=False) if json_ld else '',
    }


def _website_json_ld(request):
    base = request.build_absolute_uri('/')
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': SITE_NAME,
        'alternateName': 'Quran Online',
        'url': base,
        'inLanguage': 'id',
        'description': DEFAULT_DESCRIPTION,
        'publisher': {
            '@type': 'Organization',
            'name': SITE_NAME,
            'logo': request.build_absolute_uri(static('images/logoquran.png')),
        },
    }


def index(request):
    surahs = Surah.objects.all().prefetch_related('verses')
    total_surahs = surahs.count()
    total_verses = sum(s.number_of_verses for s in surahs)
    seo = _seo(
        request,
        title="Quran Kareem — Al-Qur'an Online 30 Juz & 114 Surah",
        path='/',
        json_ld=_website_json_ld(request),
    )
    return render(request, 'quran/index.html', {
        'surahs': surahs,
        'total_surahs': total_surahs,
        'total_verses': total_verses,
        **seo,
    })


def surah_detail(request, surah_number):
    surahs = Surah.objects.all().prefetch_related('verses')
    surah_data = get_object_or_404(Surah.objects.prefetch_related('verses'), number=surah_number)
    prev_surah = surah_number - 1 if surah_number > 1 else None
    next_surah = surah_number + 1 if surah_number < 114 else None
    all_surahs = list(surahs)

    canonical_path = reverse('surah_detail', args=[surah_number])
    title = (
        f"Surah {surah_data.name_translit_id} "
        f"({surah_data.name_translation_id}) — {surah_data.number_of_verses} Ayat"
    )
    description = (
        f"Baca Surah {surah_data.name_translit_id} ({surah_data.name_translation_id}) "
        f"lengkap {surah_data.number_of_verses} ayat, tergolong {surah_data.revelation}. "
        "Teks Arab, transliterasi, dan terjemahan bahasa Indonesia."
    )
    chapter = {
        '@context': 'https://schema.org',
        '@type': 'Chapter',
        'name': surah_data.name_translit_id,
        'alternateName': surah_data.name_arab_short,
        'position': surah_data.number,
        'inLanguage': 'ar',
        'description': description,
        'url': request.build_absolute_uri(canonical_path),
        'isPartOf': {
            '@type': 'Book',
            'name': "Al-Qur'an",
            'inLanguage': 'ar',
        },
    }
    breadcrumb = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': 1,
                'name': 'Beranda',
                'item': request.build_absolute_uri('/'),
            },
            {
                '@type': 'ListItem',
                'position': 2,
                'name': f"Surah {surah_data.name_translit_id}",
                'item': request.build_absolute_uri(canonical_path),
            },
        ],
    }
    seo = _seo(
        request,
        title=f"{title} | {SITE_NAME}",
        description=description,
        path=canonical_path,
        seo_type='article',
        json_ld=[chapter, breadcrumb],
    )

    return render(request, 'quran/surah.html', {
        'surah_data': surah_data,
        'surahs': all_surahs,
        'prev_surah': prev_surah,
        'next_surah': next_surah,
        **seo,
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
    seo = _seo(
        request,
        title=f"Credit & Sumber Data — {SITE_NAME}",
        description=(
            "Sumber data dan kredit aplikasi Quran Kareem: data Al-Qur'an, "
            "font Arab Amiri, logo, dan teknologi yang digunakan."
        ),
        path=reverse('credit'),
    )
    return render(request, 'quran/credit.html', seo)


def _country_flag(code):
    """Ubah kode negara ISO (mis. ID) menjadi emoji bendera."""
    if not code or len(code) != 2 or not code.isalpha():
        return '🌐'
    return ''.join(chr(0x1F1E6 + ord(char) - ord('A')) for char in code.upper())


def _cleanup_old_logs():
    """Bersihkan log lama setiap kali dashboard dibuka (auto-retensi)."""
    days = getattr(settings, 'STATS_RETENTION_DAYS', 90)
    if days <= 0:
        return
    cutoff = timezone.now() - timedelta(days=days)
    AccessLog.objects.filter(created_at__lt=cutoff).delete()


@staff_member_required(login_url='/admin/login/')
def stats(request):
    """Dashboard statistik visitor. Hanya untuk staff + token rahasia dari .env."""
    key = request.GET.get('key', '')
    if not settings.STATS_SECRET_KEY or key != settings.STATS_SECRET_KEY:
        # Sembunyikan keberadaan halaman dari yang tidak tahu token.
        raise Http404

    _cleanup_old_logs()

    now = timezone.localtime()
    today = now.date()
    start = today - timedelta(days=29)

    qs = AccessLog.objects.all()

    total_views = qs.count()
    total_visitors = qs.values('ip').distinct().count()

    today_qs = qs.filter(created_at__date=today)
    today_views = today_qs.count()
    today_visitors = today_qs.values('ip').distinct().count()

    # Kunjungan harian 30 hari terakhir.
    daily_rows = (
        qs.filter(created_at__date__gte=start)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(views=Count('id'), visitors=Count('ip', distinct=True))
        .order_by('day')
    )
    daily_map = {row['day']: row for row in daily_rows}
    daily_labels, daily_views, daily_visitors = [], [], []
    for offset in range(30):
        day = start + timedelta(days=offset)
        row = daily_map.get(day)
        daily_labels.append(day.strftime('%d %b'))
        daily_views.append(row['views'] if row else 0)
        daily_visitors.append(row['visitors'] if row else 0)

    # Negara teratas berdasarkan jumlah visitor unik.
    countries = list(
        qs.values('country_code', 'country_name')
        .annotate(visitors=Count('ip', distinct=True), views=Count('id'))
        .order_by('-visitors', '-views')[:10]
    )
    for country in countries:
        country['country_name'] = country['country_name'] or 'Tidak diketahui'
        country['flag'] = _country_flag(country['country_code'])

    # Halaman yang paling sering dibuka.
    top_pages = list(
        qs.values('path')
        .annotate(views=Count('id'), visitors=Count('ip', distinct=True))
        .order_by('-views', '-visitors')[:10]
    )

    # Jam paling ramai (mengikuti TIME_ZONE = Asia/Jakarta / WIB).
    hourly_rows = (
        qs.annotate(hour=ExtractHour('created_at'))
        .values('hour')
        .annotate(views=Count('id'))
        .order_by('hour')
    )
    hourly_map = {row['hour']: row['views'] for row in hourly_rows}
    hourly_labels = [f"{hour:02d}:00" for hour in range(24)]
    hourly_views = [hourly_map.get(hour, 0) for hour in range(24)]

    context = {
        'total_views': total_views,
        'total_visitors': total_visitors,
        'today_views': today_views,
        'today_visitors': today_visitors,
        'countries': countries,
        'top_pages': top_pages,
        'daily_labels': daily_labels,
        'daily_views': daily_views,
        'daily_visitors': daily_visitors,
        'hourly_labels': hourly_labels,
        'hourly_views': hourly_views,
        'generated_at': now,
        'retention_days': getattr(settings, 'STATS_RETENTION_DAYS', 90),
        **_seo(
            request,
            title=f"Statistik Visitor — {SITE_NAME}",
            description='Dashboard statistik kunjungan aplikasi Quran Kareem.',
            path=request.path,
            robots='noindex, nofollow',
        ),
    }
    return render(request, 'quran/stats.html', context)


def robots_txt(request):
    """robots.txt: izinkan crawler umum & crawler AI (GEO)."""
    stats_path = f"/{settings.STATS_URL.strip('/')}/" if settings.STATS_URL else '/stats/'
    ai_agents = [
        'GPTBot', 'ChatGPT-User', 'OAI-SearchBot', 'ClaudeBot', 'anthropic-ai',
        'PerplexityBot', 'Google-Extended', 'CCBot', 'Applebot-Extended',
        'cohere-ai', 'meta-externalagent',
    ]
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        f'Disallow: {stats_path}',
        '',
        '# Izinkan crawler AI (Generative Engine Optimization)',
    ]
    for agent in ai_agents:
        lines += [f'User-agent: {agent}', 'Allow: /', '']
    lines.append(f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}")
    lines.append('')
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


def sitemap_xml(request):
    """Sitemap dinamis berisi beranda, credit, dan seluruh surah."""
    surahs = Surah.objects.all()
    return render(
        request,
        'quran/sitemap.xml',
        {'surahs': surahs},
        content_type='application/xml',
    )


def llms_txt(request):
    """llms.txt: ringkasan situs untuk mesin pencari berbasis AI (GEO)."""
    base = request.build_absolute_uri('/')
    surahs = Surah.objects.all()
    lines = [
        f'# {SITE_NAME}',
        '',
        "> Quran Kareem adalah aplikasi Al-Qur'an online gratis berbahasa Indonesia. "
        'Menyediakan 114 surah lengkap dengan teks Arab, transliterasi, dan '
        'terjemahan bahasa Indonesia, serta penanda Makkiyah/Madaniyah.',
        '',
        '## Halaman utama',
        f'- [Beranda]({base}): daftar 114 surah Al-Qur\'an.',
        f'- [Credit]({base}credit): sumber data dan kredit aplikasi.',
        '',
        '## Daftar Surah',
    ]
    for surah in surahs:
        lines.append(
            f"- [Surah {surah.number}. {surah.name_translit_id} "
            f"({surah.name_translation_id})]({base}surah/{surah.number}/): "
            f"{surah.number_of_verses} ayat, {surah.revelation}."
        )
    lines += [
        '',
        '## Catatan',
        "- Bahasa konten: Arab (teks) dan Indonesia (terjemahan).",
        '- Sumber data: github.com/gadingnst/quran-api.',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
