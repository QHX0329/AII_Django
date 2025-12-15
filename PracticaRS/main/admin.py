from django.contrib import admin

# Register your models here.

admin.site.site_header = "Administración de AnimeRS"
admin.site.site_title = "AnimeRS Admin"
admin.site.index_title = "Panel de Administración de AnimeRS"
from .models import Anime, Puntuacion
admin.site.register(Anime)
admin.site.register(Puntuacion)