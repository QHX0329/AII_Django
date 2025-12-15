# main/recommendations.py
from main.models import Puntuacion
from math import sqrt
import shelve

# c) Distancia Euclidea (Inversa para que mayor sea más similar)
def sim_euclidean(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    
    if len(si) == 0: return 0

    sum_of_squares = sum([pow(prefs[p1][item] - prefs[p2][item], 2) 
                          for item in prefs[p1] if item in prefs[p2]])
    
    return 1 / (1 + sqrt(sum_of_squares))

# Carga de datos en diccionario para el algoritmo
def load_dict():
    prefs = {}
    # Iteramos sobre todas las puntuaciones para construir la matriz Usuario-Item
    for p in Puntuacion.objects.all():
        prefs.setdefault(p.id_usuario, {})
        prefs[p.id_usuario][p.anime_id] = float(p.puntuacion)
    
    shelf = shelve.open("dataRS.dat")
    shelf['prefs'] = prefs
    shelf.close()
    print("Diccionario de preferencias cargado y guardado en 'dataRS.dat'")

# Función auxiliar para invertir preferencias (Item-Usuario) para apartado d)
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result

# Encuentra los items más parecidos (Apartado d)
def topMatches(prefs, person, n=5, similarity=sim_euclidean):
    scores = [(similarity(prefs, person, other), other) 
              for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

# Recomendar usuarios para un item (Apartado e)
# Estrategia: Predecir el rating que daría cada usuario U al item I
# Devolvemos los usuarios con mayor predicción estimada
def get_users_for_item(prefs, item_id):
    user_scores = []
    
    # Recorremos todos los usuarios
    for user in prefs:
        # Si el usuario ya lo puntuó, no lo recomendamos (o sí, según interpretación, 
        # pero normalmente se recomiendan "nuevos" candidatos)
        if item_id in prefs[user]:
            continue
            
        # Predecimos puntuación usando media ponderada por similitud con otros usuarios
        total = 0
        simSum = 0
        
        # Comparamos con otros usuarios que SÍ han puntuado el item
        # Optimización: iteramos solo usuarios relevantes si fuera posible, 
        # aquí iteramos dataset completo (puede ser lento con muchos users)
        for other in prefs:
            if other == user: continue
            if item_id not in prefs[other]: continue # Solo nos sirven los que puntuaron el item
            
            sim = sim_euclidean(prefs, user, other)
            
            if sim > 0:
                total += sim * prefs[other][item_id]
                simSum += sim
        
        if simSum > 0:
            predicted_rating = total / simSum
            user_scores.append((predicted_rating, user))
            
    # Ordenamos por mayor predicción
    user_scores.sort(key=lambda x: x[0], reverse=True)
    return user_scores[:5]