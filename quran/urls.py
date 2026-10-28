from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('surah', views.surah_php, name='surah_php'),
    path('surah/<int:surah_number>/', views.surah_detail, name='surah_detail'),
    path('credit', views.credit, name='credit'),
]
