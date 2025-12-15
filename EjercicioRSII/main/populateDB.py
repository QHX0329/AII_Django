# main/populateDB.py
from main.models import Usuario, Artista, Etiqueta, UsuarioArtista, UsuarioEtiquetaArtista
from django.db.models import Count

path = "data"

def populate():
    print("Cargando Artistas...")
    populateArtistas()
    print("Cargando Etiquetas...")
    populateEtiquetas()
    print("Cargando Usuarios y Relaciones...")
    populateUsuariosYRelaciones()
    print("Calculando y almacenando etiquetas frecuentes de artistas...")
    calculateArtistTags()
    print("Carga finalizada.")

def populateArtistas():
    Artista.objects.all().delete()
    lista = []
    # Formato esperado: id \t name \t url \t pictureURL
    with open(path + "/artists.dat", "r", encoding='utf-8') as f:
        next(f) # Saltar cabecera si existe
        for line in f:
            rip = line.strip().split('\t')
            # Asegurar que hay suficientes columnas
            if len(rip) >= 4:
                lista.append(Artista(idArtista=rip[0], nombre=rip[1], url=rip[2], pictureUrl=rip[3]))
    Artista.objects.bulk_create(lista)

def populateEtiquetas():
    Etiqueta.objects.all().delete()
    lista = []
    # Formato esperado: tagID \t tagValue
    with open(path + "/tags.dat", "r", encoding='utf-8') as f:
        next(f)
        for line in f:
            rip = line.strip().split('\t')
            if len(rip) >= 2:
                lista.append(Etiqueta(idTag=rip[0], tagValue=rip[1]))
    Etiqueta.objects.bulk_create(lista)

def populateUsuariosYRelaciones():
    # Borramos tablas dependientes primero
    UsuarioArtista.objects.all().delete()
    UsuarioEtiquetaArtista.objects.all().delete()
    Usuario.objects.all().delete()

    # 1. Recuperamos los IDs de Artistas y Etiquetas que SI existen en la BD
    # Usamos sets para que la búsqueda sea ultra-rápida
    existing_artists = set(Artista.objects.values_list('idArtista', flat=True))
    existing_tags = set(Etiqueta.objects.values_list('idTag', flat=True))

    users_set = set()
    lista_ua = []
    
    print("Procesando user_artists.dat...")
    # Carga UsuarioArtista
    with open(path + "/user_artists.dat", "r", encoding='utf-8') as f:
        next(f)
        for line in f:
            rip = line.strip().split('\t')
            if len(rip) >= 3:
                u_id, a_id, weight = rip[0], rip[1], rip[2]
                
                # VERIFICACIÓN DE INTEGRIDAD: Solo añadimos si el artista existe
                if a_id in existing_artists:
                    users_set.add(u_id)
                    lista_ua.append(UsuarioArtista(idUsuario_id=u_id, idArtista_id=a_id, tiempoEscucha=int(weight)))
                else:
                    # Opcional: imprimir qué artistas fallan
                    pass 
    
    lista_uta = []
    print("Procesando user_taggedartists.dat...")
    # Carga UsuarioEtiquetaArtista
    with open(path + "/user_taggedartists.dat", "r", encoding='utf-8') as f:
        next(f)
        for line in f:
            rip = line.strip().split('\t')
            if len(rip) >= 6:
                u_id, a_id, t_id = rip[0], rip[1], rip[2]
                
                # VERIFICACIÓN DE INTEGRIDAD: Validamos artista y etiqueta
                if a_id in existing_artists and t_id in existing_tags:
                    users_set.add(u_id)
                    lista_uta.append(UsuarioEtiquetaArtista(
                        idUsuario_id=u_id, 
                        idArtista_id=a_id, 
                        idTag_id=t_id, 
                        dia=int(rip[3]), 
                        mes=int(rip[4]), 
                        anyo=int(rip[5])
                    ))

    # Crear Usuarios únicos
    Usuario.objects.bulk_create([Usuario(idUsuario=uid) for uid in users_set])
    
    # Crear relaciones masivamente
    UsuarioArtista.objects.bulk_create(lista_ua)

    UsuarioEtiquetaArtista.objects.bulk_create(lista_uta)
    
def calculateArtistTags():
    # "Para establecer las características de los artistas establecer las diez etiquetas más
    # frecuentes que los usuarios le han dado a cada artista y almacenarlas."
    
    # Iteramos sobre todos los artistas que han sido etiquetados
    artistas = Artista.objects.all()
    for artista in artistas:
        # Obtenemos las etiquetas más usadas para este artista
        top_tags = UsuarioEtiquetaArtista.objects.filter(idArtista=artista).values('idTag').annotate(
            count=Count('idTag')).order_by('-count')[:10]
        
        tags_objs = [Etiqueta.objects.get(idTag=t['idTag']) for t in top_tags]
        artista.etiquetas.set(tags_objs)