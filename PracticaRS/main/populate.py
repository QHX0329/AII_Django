import csv
import os
from main.models import Anime, Puntuacion

path = "data" 
FICH_ANIME = "anime.csv"
FICH_RATING = "ratings.csv"

def populate_database():
    delete_tables()
    dict_animes = populate_animes()
    populate_ratings(dict_animes)
    print("Base de datos cargada correctamente.")

def delete_tables():
    Puntuacion.objects.all().delete()
    Anime.objects.all().delete()
    print("Tablas borradas.")

def populate_animes():
    print("Eliminando datos anteriores de Animes y Puntuaciones...")
    Puntuacion.objects.all().delete()
    Anime.objects.all().delete()
    
    print("Cargando animes...")
    lista_animes = []
    dict_animes = {}
    
    ruta_fichero = os.path.join(path, FICH_ANIME)
    
    if not os.path.exists(ruta_fichero):
        print(f"ERROR: No se encuentra el archivo {ruta_fichero}")
        return {}

    with open(ruta_fichero, encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=';') 
        
        next(reader)
        
        for row in reader:
            if len(row) < 5: continue 
            
            try:
                aid = int(row[0])
                titulo = row[1]
                generos = row[2]
                formato = row[3]
                
                episodios_str = row[4].strip()
                if episodios_str.isdigit():
                    episodios = int(episodios_str)
                else:
                    episodios = 0
                
                obj_anime = Anime(
                    anime_id=aid,
                    titulo=titulo,
                    generos=generos,
                    formato_emision=formato,
                    num_episodios=episodios
                )
                
                lista_animes.append(obj_anime)
                dict_animes[aid] = obj_anime
            except ValueError:
                continue

    Anime.objects.bulk_create(lista_animes)
    print(f"Animes insertados: {len(lista_animes)}")
    
    return dict_animes

def populate_ratings(dict_animes):
    print("Cargando puntuaciones...")
    lista_puntuaciones = []
    
    ruta_fichero = os.path.join(path, FICH_RATING)
    
    if not os.path.exists(ruta_fichero):
        print(f"ERROR: No se encuentra el archivo {ruta_fichero}")
        return

    with open(ruta_fichero, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';') 
        next(reader)
        
        count = 0
        for row in reader:
            if len(row) < 3: continue
            
            try:
                uid = int(row[0])
                aid = int(row[1])
                rating = int(row[2])
            except ValueError:
                continue 
            
            if rating > 0 and aid in dict_animes:
                obj_puntuacion = Puntuacion(
                    id_usuario=uid,
                    anime=dict_animes[aid],
                    puntuacion=rating
                )
                lista_puntuaciones.append(obj_puntuacion)
                count += 1
                
            if len(lista_puntuaciones) >= 50000:
                Puntuacion.objects.bulk_create(lista_puntuaciones)
                lista_puntuaciones = []
                print(f"Procesadas {count} puntuaciones...")

    if lista_puntuaciones:
        Puntuacion.objects.bulk_create(lista_puntuaciones)
    
    print(f"Total Puntuaciones insertadas: {Puntuacion.objects.count()}")