from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from main.models import Anime, Puntuacion
from main.forms import CargaForm, FormatoEmisionForm, AnimeBusquedaForm
from main.populate import populate_database
from main.recommendations import load_dict, transformPrefs, topMatches, get_users_for_item, sim_euclidean
import shelve

def index(request):
    return render(request, 'index.html')

def carga(request):
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            populate_database()
            num_animes = Anime.objects.count()
            num_puntuaciones = Puntuacion.objects.count()
            mensaje = f"Carga finalizada. Animes: {num_animes}, Puntuaciones: {num_puntuaciones}"
            return render(request, 'carga.html', {'mensaje': mensaje})
    return render(request, 'carga.html', {'form': CargaForm()})

def load_rs(request):
    load_dict()
    return render(request, 'load_rs.html', {'mensaje': "Datos del Sistema de Recomendación cargados correctamente."})

def animes_por_formato(request):
    animes = None
    form = FormatoEmisionForm()
    
    if request.method == 'POST':
        form = FormatoEmisionForm(request.POST)
        if form.is_valid():
            formato = form.cleaned_data['formato']
            animes = Anime.objects.filter(formato_emision=formato).order_by('-num_episodios')
            
    return render(request, 'animes_por_formato.html', {'form': form, 'animes': animes})

def animes_populares(request):
    top_animes_data = Puntuacion.objects.values('anime').annotate(num_votos=Count('anime')).order_by('-num_votos')[:3]
    
    resultados = []
    
    shelf = shelve.open("dataRS.dat")
    prefs = shelf.get('prefs', {})
    shelf.close()
    
    item_prefs = transformPrefs(prefs)
    
    for item in top_animes_data:
        anime_id = item['anime']
        anime_obj = Anime.objects.get(anime_id=anime_id)
        
        similares_ids = topMatches(item_prefs, anime_id, n=3, similarity=sim_euclidean)
        
        similares_objs = []
        for score, sim_id in similares_ids:
            try:
                sim_obj = Anime.objects.get(anime_id=sim_id)
                similares_objs.append({'titulo': sim_obj.titulo, 'similitud': round(score, 4)})
            except Anime.DoesNotExist:
                continue
                
        resultados.append({
            'anime': anime_obj,
            'votos': item['num_votos'],
            'similares': similares_objs
        })
        
    return render(request, 'animes_populares.html', {'resultados': resultados})

def recomendar_usuarios(request):
    usuarios_recomendados = None
    anime_seleccionado = None
    form = AnimeBusquedaForm()
    
    if request.method == 'POST':
        form = AnimeBusquedaForm(request.POST)
        if form.is_valid():
            anime_id = form.cleaned_data['anime_id']
            try:
                anime_seleccionado = Anime.objects.get(anime_id=anime_id)
                
                shelf = shelve.open("dataRS.dat")
                prefs = shelf.get('prefs', {})
                shelf.close()
                
                if not prefs:
                    return render(request, 'recomendar_usuarios.html', {'form': form, 'error': "Primero debes cargar el RecSys"})

                recs = get_users_for_item(prefs, anime_id)
                usuarios_recomendados = recs
                
            except Anime.DoesNotExist:
                form.add_error('anime_id', "El Anime con ese ID no existe.")
                
    return render(request, 'recomendar_usuarios.html', {'form': form, 'usuarios': usuarios_recomendados, 'anime': anime_seleccionado})
