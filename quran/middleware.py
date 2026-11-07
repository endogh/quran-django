"""Middleware untuk mencatat kunjungan visitor ke dashboard statistik."""

import ipaddress
import logging
import re

import requests
from django.conf import settings

from .models import AccessLog, IPGeoCache

logger = logging.getLogger(__name__)

# Path yang tidak perlu dicatat sebagai kunjungan.
EXCLUDED_PREFIXES = (
    '/admin/', '/static/', '/favicon.ico', '/robots.txt',
    '/sitemap.xml', '/llms.txt',
)

# User-agent bot/crawler tidak dihitung sebagai visitor manusia.
BOT_PATTERN = re.compile(
    r'bot|crawler|spider|crawl|slurp|mediapartners|facebookexternalhit|'
    r'curl|wget|python-requests|headlesschrome',
    re.IGNORECASE,
)

# ip-api.com gratis (tanpa API key). Hasil di-cache di tabel IPGeoCache.
GEO_API_URL = 'http://ip-api.com/json/{ip}?fields=status,country,countryCode'
GEO_API_TIMEOUT = 1.5


def get_client_ip(request):
    """Ambil IP asli visitor, mendukung nginx/CDN lewat X-Forwarded-For."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        # Format: "client, proxy1, proxy2" -> ambil yang paling depan.
        return xff.split(',')[0].strip()
    x_real = request.META.get('HTTP_X_REAL_IP')
    if x_real:
        return x_real.strip()
    return request.META.get('REMOTE_ADDR', '').strip()


def _is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True


def resolve_country(ip):
    """Kembalikan (country_code, country_name) untuk sebuah IP.

    Hasil disimpan di IPGeoCache sehingga API hanya dipanggil sekali per IP.
    """
    if not ip or _is_private_ip(ip):
        return '', 'Lokal'

    cached = IPGeoCache.objects.filter(ip=ip).first()
    if cached:
        return cached.country_code, cached.country_name

    code, name = '', 'Tidak diketahui'
    resolved = False
    try:
        resp = requests.get(GEO_API_URL.format(ip=ip), timeout=GEO_API_TIMEOUT)
        data = resp.json()
        if data.get('status') == 'success':
            code = data.get('countryCode', '') or ''
            name = data.get('country', '') or 'Tidak diketahui'
            resolved = True
        elif data.get('status') == 'fail':
            # IP valid tetapi tidak punya data negara -> cache sebagai unknown.
            resolved = True
    except Exception as exc:  # noqa: BLE001 - jangan sampai request ikut gagal
        logger.warning("Gagal resolve geo IP %s: %s", ip, exc)

    if resolved:
        IPGeoCache.objects.update_or_create(
            ip=ip, defaults={'country_code': code, 'country_name': name}
        )
    return code, name


class TrackVisitsMiddleware:
    """Catat setiap kunjungan halaman (GET) ke tabel AccessLog."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_prefixes = list(EXCLUDED_PREFIXES)
        # Path dashboard statistik juga tidak perlu dicatat.
        if settings.STATS_URL:
            self.excluded_prefixes.append(f"/{settings.STATS_URL.strip('/')}/")

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._track(request)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Tracking kunjungan gagal: %s", exc)
        return response

    def _track(self, request):
        if request.method != 'GET':
            return

        path = request.path
        if any(path.startswith(prefix) for prefix in self.excluded_prefixes):
            return

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if BOT_PATTERN.search(user_agent):
            return

        ip = get_client_ip(request)
        code, name = resolve_country(ip)
        AccessLog.objects.create(
            ip=ip or '0.0.0.0',
            country_code=code,
            country_name=name,
            path=path[:255],
            user_agent=user_agent[:255],
        )
