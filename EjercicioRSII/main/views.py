# main/views.py
from django.shortcuts import render, get_object_or_404
from main.models import Usuario, Artista, UsuarioArtista, UsuarioEtiquetaArtista
from main.forms import UsuarioBusquedaForm, ArtistaBusquedaForm
from main.populateDB import populate
from main.recommendations import recommend_artists
from django.db.models import Count

def index(request):
    return render(request, 'index.html')

def carga(request):
    populate()
    return render(request, 'carga.html')

# a) Dado un usuario, artistas más escuchados
def artistas_mas_escuchados(request):
    formulario = UsuarioBusquedaForm()
    artistas = None
    usuario = None
    
    if request.method == 'POST':
        formulario = UsuarioBusquedaForm(request.POST)
        if formulario.is_valid():
            id_usuario = formulario.cleaned_data['idUsuario']
            try:
                usuario = Usuario.objects.get(idUsuario=id_usuario)
                artistas = UsuarioArtista.objects.filter(idUsuario=usuario).order_by('-tiempoEscucha')[:5]
            except Usuario.DoesNotExist:
                formulario.add_error('idUsuario', 'El usuario no existe')

    return render(request, 'artistas_mas_escuchados.html', {'formulario': formulario, 'artistas': artistas, 'usuario': usuario})

# b) Dado un artista, etiquetas más frecuentes
def etiquetas_artista(request):
    formulario = ArtistaBusquedaForm()
    etiquetas = None
    artista = None
    
    if request.method == 'POST':
        formulario = ArtistaBusquedaForm(request.POST)
        if formulario.is_valid():
            id_artista = formulario.cleaned_data['idArtista']
            try:
                artista = Artista.objects.get(idArtista=id_artista)
                # Obtenemos las etiquetas directamente de la relación calculada en populate
                # o calculándolas al vuelo si se prefiere ver el detalle crudo
                etiquetas = UsuarioEtiquetaArtista.objects.filter(idArtista=artista).values('idTag__tagValue').annotate(
                    frecuencia=Count('idTag')).order_by('-frecuencia')[:10]
            except Artista.DoesNotExist:
                formulario.add_error('idArtista', 'El artista no existe')

    return render(request, 'etiquetas_artista.html', {'formulario': formulario, 'etiquetas': etiquetas, 'artista': artista})

# c) Recomendación de artistas
def recomendacion_usuarios(request):
    formulario = UsuarioBusquedaForm()
    recomendaciones = None
    usuario = None
    
    if request.method == 'POST':
        formulario = UsuarioBusquedaForm(request.POST)
        if formulario.is_valid():
            id_usuario = formulario.cleaned_data['idUsuario']
            try:
                usuario = Usuario.objects.get(idUsuario=id_usuario)
                recomendaciones = recommend_artists(usuario)
            except Usuario.DoesNotExist:
                formulario.add_error('idUsuario', 'El usuario no existe')

    return render(request, 'recomendacion_usuarios.html', {'formulario': formulario, 'recomendaciones': recomendaciones})
