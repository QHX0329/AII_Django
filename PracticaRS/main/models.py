from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Anime(models.Model):
    animeID = models.IntegerField(primary_key=True)  # ID del dataset
    titulo = models.TextField(verbose_name='Título')
    generos = models.TextField(verbose_name='Géneros') # Lista separada por comas o pipes
    formato = models.CharField(max_length=50, verbose_name='Formato') # TV, Movie, etc.
    episodios = models.IntegerField(verbose_name='Número de episodios')

    def __str__(self):
        return self.titulo
    
class Puntuacion(models.Model):
    idUsuario = models.IntegerField(verbose_name='Id Usuario') 
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(
        verbose_name='Puntuación', 
        validators=[MinValueValidator(1), MaxValueValidator(10)] # [cite: 3039]
    )
    
    class Meta:
        unique_together = ('idUsuario', 'anime')