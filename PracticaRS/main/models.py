from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Anime(models.Model):
    anime_id = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name='Título')
    generos = models.CharField(max_length=500, verbose_name='Géneros')
    formato_emision = models.CharField(max_length=50, verbose_name='Formato de emisión') # TV, Movie, OVA...
    num_episodios = models.IntegerField(verbose_name='Número de episodios', default=0)

    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('titulo', )

class Puntuacion(models.Model):
    id_usuario = models.IntegerField(verbose_name='Id Usuario')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(verbose_name='Puntuación', 
        validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.id_usuario} - {self.anime} - {self.puntuacion}"
    
    class Meta:
        ordering = ('id_usuario', 'anime')
