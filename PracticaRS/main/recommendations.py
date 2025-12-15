from main.models import Puntuacion
from math import sqrt
import shelve

def sim_euclidean(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    
    if len(si) == 0: return 0

    sum_of_squares = sum([pow(prefs[p1][item] - prefs[p2][item], 2) 
        for item in prefs[p1] if item in prefs[p2]])
    
    return 1 / (1 + sqrt(sum_of_squares))

def load_dict():
    prefs = {}
    for p in Puntuacion.objects.all():
        prefs.setdefault(p.id_usuario, {})
        prefs[p.id_usuario][p.anime_id] = float(p.puntuacion)
    
    shelf = shelve.open("dataRS.dat")
    shelf['prefs'] = prefs
    shelf.close()
    print("Diccionario de preferencias cargado y guardado en 'dataRS.dat'")

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result

def topMatches(prefs, person, n=5, similarity=sim_euclidean):
    scores = [(similarity(prefs, person, other), other) 
        for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def get_users_for_item(prefs, item_id):
    user_scores = []
    
    for user in prefs:
        if item_id in prefs[user]:
            continue
            
        total = 0
        simSum = 0
        
        for other in prefs:
            if other == user: continue
            if item_id not in prefs[other]: continue
            
            sim = sim_euclidean(prefs, user, other)
            
            if sim > 0:
                total += sim * prefs[other][item_id]
                simSum += sim
        
        if simSum > 0:
            predicted_rating = total / simSum
            user_scores.append((predicted_rating, user))
            
    user_scores.sort(key=lambda x: x[0], reverse=True)
    return user_scores[:5]