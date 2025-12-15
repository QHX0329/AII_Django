# main/urls.py
from django.urls import path
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('carga/', views.carga, name='carga'),
    path('loadRS/', views.load_rs, name='load_rs'),
    path('animes_formato/', views.animes_por_formato, name='animes_por_formato'),
    path('animes_populares/', views.animes_populares, name='animes_populares'),
    path('recomendar_usuarios/', views.recomendar_usuarios, name='recomendar_usuarios'),
]
