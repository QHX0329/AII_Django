from django.contrib import admin
from django.urls import path
from main import views  # Importante: asegurate de que esta linea no da error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Ruta para la página de inicio
    path('carga/', views.carga, name='carga'),
    path('artistas_mas_escuchados/', views.artistas_mas_escuchados, name='artistas_mas_escuchados'),
    path('etiquetas_artista/', views.etiquetas_artista, name='etiquetas_artista'),
    path('recomendacion_usuarios/', views.recomendacion_usuarios, name='recomendacion_usuarios'),
]
