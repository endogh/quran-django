from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('surah', views.surah_php, name='surah_php'),
    path('surah/<int:surah_number>/', views.surah_detail, name='surah_detail'),
    path('credit', views.credit, name='credit'),

    # SEO / GEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('llms.txt', views.llms_txt, name='llms_txt'),
]

# Dashboard statistik memakai path rahasia dari .env (STATS_URL).
if settings.STATS_URL:
    urlpatterns += [
        path(f"{settings.STATS_URL.strip('/')}/", views.stats, name='stats'),
    ]
