from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('cargar/', views.cargar, name='cargar'),
    path('loadRS/', views.loadRS, name='loadRS'),
    path('animes_formato/', views.animes_por_formato, name='animes_formato'),
    path('populares/', views.animes_populares, name='populares'),
    path('recomendar_usuarios/', views.recomendar_usuarios, name='recomendar_usuarios'),
]