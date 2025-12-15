from django.shortcuts import render

# Create your views here.
#encoding:utf-8
from django.shortcuts import render, redirect, get_object_or_404
from main.models import Anime, Puntuacion
from main.forms import AnimeBusquedaForm, FormatoBusquedaForm
from main import populateBD
from main.recommendations import transformPrefs, getRecommendations, topMatches, sim_distance
import shelve
from django.db.models import Count

# 1. Cargar BD
def cargar(request):
    mensaje = ""
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            populateBD.populate()
            num_animes = Anime.objects.count()
            num_votos = Puntuacion.objects.count()
            mensaje = f"Base de datos cargada: {num_animes} animes y {num_votos} puntuaciones."
    
    return render(request, 'cargar.html', {'mensaje': mensaje})

# 2. Cargar RecSys (Generar archivo Shelve)
def loadRS(request):
    if request.method == 'POST': # Solo cargar si se pulsa el botón
        print("Generando fichero dataRS...")
        Prefs = {}
        # Cargamos puntuaciones en memoria
        ratings = Puntuacion.objects.all()
        for ra in ratings:
            user = int(ra.idUsuario)
            item = int(ra.anime.animeID)
            rating = float(ra.puntuacion)
            
            Prefs.setdefault(user, {})
            Prefs[user][item] = rating
            
        # Guardamos en disco
        shelf = shelve.open("dataRS.dat")
        shelf['Prefs'] = Prefs
        shelf['ItemsPrefs'] = transformPrefs(Prefs) # Matriz invertida (Item -> Usuarios)
        shelf.close()
        print("Fichero dataRS generado correctamente.")
        return render(request, 'loadRS.html', {'mensaje': "Sistema de recomendación cargado correctamente"})
        
    return render(request, 'loadRS.html')

# 3. Animes por Formato (Spinbox)
def animes_por_formato(request):
    formulario = FormatoBusquedaForm()
    animes = None
    formato_seleccionado = None
    
    if request.method == 'POST':
        formulario = FormatoBusquedaForm(request.POST)
        if formulario.is_valid():
            formato_seleccionado = formulario.cleaned_data['formato']
            # Filtramos y ordenamos por episodios (descendente)
            animes = Anime.objects.filter(formato=formato_seleccionado).order_by('-episodios')
            
    return render(request, 'animes_formato.html', {
        'formulario': formulario, 
        'animes': animes, 
        'formato': formato_seleccionado
    })

# 4. Animes Populares y Similares (Distancia Euclidea)
def animes_populares(request):
    # Top 3 animes con más puntuaciones
    top_animes = Anime.objects.annotate(num_votos=Count('puntuacion')).order_by('-num_votos')[:3]
    
    resultados = []
    
    # Abrimos shelve para buscar similares
    shelf = shelve.open("dataRS.dat")
    ItemsPrefs = shelf.get('ItemsPrefs', {}) # Usamos la matriz de Items
    shelf.close()
    
    if not ItemsPrefs:
        return render(request, 'error.html', {'mensaje': 'Error: Cargue el RecSys primero'})

    for anime in top_animes:
        # Buscamos los 3 más parecidos usando distancia Euclidiana
        # Nota: topMatches usa los IDs, hay que buscar los objetos después
        similares_ids = topMatches(ItemsPrefs, int(anime.animeID), n=3, similarity=sim_distance)
        
        similares_objs = []
        for score, other_id in similares_ids:
            try:
                obj = Anime.objects.get(pk=other_id)
                similares_objs.append((obj, score))
            except Anime.DoesNotExist:
                continue
                
        resultados.append({
            'anime': anime,
            'similares': similares_objs
        })
        
    return render(request, 'animes_populares.html', {'resultados': resultados})

# 5. Recomendar Usuarios para un Anime
def recomendar_usuarios(request):
    formulario = AnimeBusquedaForm()
    anime = None
    recomendaciones = []
    
    if request.method == 'POST':
        formulario = AnimeBusquedaForm(request.POST)
        if formulario.is_valid():
            id_anime = formulario.cleaned_data['idAnime']
            anime = get_object_or_404(Anime, pk=id_anime)
            
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf.get('ItemsPrefs', {})
            shelf.close()
            
            if ItemsPrefs:
                # TRUCO: Usamos getRecommendations sobre ItemsPrefs pasando el ID del anime.
                # Al ser la matriz invertida, esto nos "recomienda" usuarios que encajan con este anime
                rankings = getRecommendations(ItemsPrefs, int(id_anime))
                
                # --- AÑADE ESTO PARA DEPURAR ---
                print(f"Total predicciones: {len(rankings)}")
                print(f"Top 5: {rankings[:5]}")
                print(f"Predicciones del puesto 50 al 55: {rankings[50:55]}") # Mira más abajo
                # -------------------------------
                
                # Cogemos los 5 mejores
                top_5 = rankings[:5]
                recomendaciones = top_5 # Lista de tuplas (score, idUsuario)
                
    return render(request, 'recomendar_usuarios.html', {
        'formulario': formulario, 
        'anime': anime, 
        'recomendaciones': recomendaciones
    })

def inicio(request):
    return render(request, 'index.html')