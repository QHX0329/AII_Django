# main/models.py
#encoding:utf-8

from django.db import models

class Etiqueta(models.Model):
    idTag = models.TextField(primary_key=True)
    tagValue = models.TextField(verbose_name='Valor de la etiqueta')

    def __str__(self):
        return self.tagValue
    
    class Meta:
        ordering = ('tagValue', )

class Artista(models.Model):
    idArtista = models.TextField(primary_key=True)
    nombre = models.TextField(verbose_name='Nombre')
    url = models.URLField(verbose_name='URL')
    pictureUrl = models.URLField(verbose_name='URL de la imagen')
    # Campo para almacenar las 10 etiquetas más frecuentes (Requisito del enunciado)
    etiquetas = models.ManyToManyField(Etiqueta, related_name='artistas_etiquetados')

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ('nombre', )

class Usuario(models.Model):
    idUsuario = models.TextField(primary_key=True)
    
    def __str__(self):
        return self.idUsuario
    
    class Meta:
        ordering = ('idUsuario', )

class UsuarioArtista(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idArtista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    tiempoEscucha = models.IntegerField(verbose_name='Tiempo de escucha')

    class Meta:
        ordering = ('idUsuario', '-tiempoEscucha')

class UsuarioEtiquetaArtista(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idArtista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    idTag = models.ForeignKey(Etiqueta, on_delete=models.CASCADE)
    dia = models.IntegerField(verbose_name='Día')
    mes = models.IntegerField(verbose_name='Mes')
    anyo = models.IntegerField(verbose_name='Año')

    class Meta:
        ordering = ('idUsuario', 'idArtista')

# Create your models here.
