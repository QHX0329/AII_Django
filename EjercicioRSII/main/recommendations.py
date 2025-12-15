# main/recommendations.py
from main.models import UsuarioArtista, Artista, Etiqueta
from django.db.models import Count

# Función para calcular coeficiente de Dice entre dos conjuntos de etiquetas
def dice_coefficient(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    return 2.0 * intersection / (len(set1) + len(set2))

def get_user_profile_tags(user):
    # "Para determinar las preferencias de un usuario, tomar los cinco artistas que más tiempo
    # ha escuchado..."
    top_artists = UsuarioArtista.objects.filter(idUsuario=user).order_by('-tiempoEscucha')[:5].values_list('idArtista', flat=True)
    
    if not top_artists:
        return set()

    # "...y obtener las diez etiquetas más frecuentes de esos artistas."
    # Buscamos las etiquetas asociadas a esos 5 artistas (usando las almacenadas en el modelo Artista)
    # y calculamos las más frecuentes globalmente para el perfil.
    tags_ids = Artista.etiquetas.through.objects.filter(artista_id__in=top_artists).values('etiqueta_id').annotate(
        count=Count('etiqueta_id')).order_by('-count')[:10]
    
    return set([t['etiqueta_id'] for t in tags_ids])

def recommend_artists(user):
    user_profile_tags = get_user_profile_tags(user)
    
    # Artistas que el usuario YA ha escuchado (para excluirlos)
    escuchados = UsuarioArtista.objects.filter(idUsuario=user).values_list('idArtista', flat=True)
    
    recommendations = []
    
    # Comparamos con todos los artistas (o una muestra si son muchos)
    all_artists = Artista.objects.exclude(idArtista__in=escuchados).prefetch_related('etiquetas')
    
    for artist in all_artists:
        artist_tags = set([tag.idTag for tag in artist.etiquetas.all()])
        
        # Calcular similitud
        sim = dice_coefficient(user_profile_tags, artist_tags)
        
        if sim > 0:
            recommendations.append((sim, artist))
            
    # Ordenar por similitud descendente
    recommendations.sort(key=lambda x: x[0], reverse=True)
    
    return recommendations[:10] # Devolver top 10 recomendaciones