# main/populate.py
import csv
import os
from main.models import Anime, Puntuacion

path = "data" 

def populate_database():
    delete_tables()
    populate_animes()
    populate_ratings()
    print("Base de datos cargada correctamente.")

def delete_tables():
    Puntuacion.objects.all().delete()
    Anime.objects.all().delete()
    print("Tablas borradas.")

def populate_animes():
    print("Cargando Animes...")
    lista_animes = []
    
    # Verificar si el archivo existe
    file_path = os.path.join(path, 'anime.csv')
    if not os.path.exists(file_path):
        print(f"ERROR: No se encuentra el archivo en {file_path}")
        return

    # Usamos 'utf-8-sig' para gestionar caracteres BOM si el CSV viene de Excel
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        # DEBUG: Imprimir las columnas detectadas para ver si coinciden
        print(f"Columnas detectadas en anime.csv: {reader.fieldnames}")

        for i, row in enumerate(reader):
            try:

                # Para que no cargue animes con el .hack u otros sin título válido
                nombre = row['name']
                if not nombre or not nombre[0].isalnum():
                    continue

                episodes_str = row.get('episodes', '0')
                episodes = int(episodes_str) if episodes_str.isdigit() else 0
                
                anime = Anime(
                    anime_id=int(row['anime_id']),
                    titulo=row['name'],
                    generos=row.get('genre', ''), # .get evita error si falta la columna
                    formato_emision=row.get('type', ''),
                    num_episodios=episodes
                )
                lista_animes.append(anime)
            except Exception as e:
                # IMPRIMIR ERROR: Solo mostramos los primeros 5 errores para no saturar
                if i < 5:
                    print(f"Error en fila {i}: {e} | Datos: {row}")
    
    Anime.objects.bulk_create(lista_animes)
    print(f"{len(lista_animes)} animes insertados.")

def populate_ratings():
    print("Cargando Puntuaciones...")
    lista_puntuaciones = []
    valid_anime_ids = set(Anime.objects.values_list('anime_id', flat=True))
    
    file_path = os.path.join(path, 'ratings.csv')
    if not os.path.exists(file_path):
        print(f"ERROR: No se encuentra el archivo en {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        count = 0
        for row in reader:
            try:
                aid = int(row['anime_id'])
                rating = int(row['rating'])
                
                if aid in valid_anime_ids and rating > 0:
                    puntuacion = Puntuacion(
                        id_usuario=int(row['user_id']),
                        anime_id=aid, # Asignamos el ID directamente, Django lo mapea si es ForeignKey
                        puntuacion=rating
                    )
                    # Como Puntuacion.anime es ForeignKey, necesitamos pasar un objeto Anime o el ID a la columna correcta
                    # En bulk_create con ForeignKey, es mejor usar la instancia o el campo _id
                    puntuacion.anime_id = aid 
                    
                    lista_puntuaciones.append(puntuacion)
                    count += 1
            except Exception as e:
                pass

            # Optimización de memoria: guardar cada 10.000 registros
            if len(lista_puntuaciones) >= 10000:
                Puntuacion.objects.bulk_create(lista_puntuaciones)
                lista_puntuaciones = []
                print(f"Procesados {count} ratings...")

    # Guardar los restantes
    if lista_puntuaciones:
        Puntuacion.objects.bulk_create(lista_puntuaciones)
    
    print(f"Total: {Puntuacion.objects.count()} puntuaciones insertadas.")