import math 
import numpy as np
from config import Config
from scipy.spatial import distance

### Middlebury
# Obtenir la liste des triangles associés à un point
def liste_tri_points(model_faces):
    """
    Produit un dictionnaire qui contient la liste de indices des triangles associés à chaque points du model.
    """
    dico = {}
    max = 0
    for ind, face in enumerate(model_faces):
        if face[0] in dico:
            dico[face[0]].append(ind)
        else:
            dico[face[0]] = [ind]
            if face[0] > max:
                max = face[0]
        
        if face[1] in dico:
            dico[face[1]].append(ind)
        else:
            dico[face[1]] = [ind]
            if face[1] > max:
                max = face[1]
        
        if face[2] in dico:
            dico[face[2]].append(ind)
        else:
            dico[face[2]] = [ind]
            if face[2] > max:
                max = face[2]
    for i in range(3*max+1):
        if i not in dico:
            dico[i] = []
    return dico

def liste_normales(model_vertices, model_faces, dico_triangles):
    """
    Produit la liste des normales associées à chaque points du model
    Il faut d'abord avoir calculé la liste des triangles associés à chaque points avec `liste_tri_points(model)`
    et le passer dans l'argument `dico_triangles`
    """
    liste = []
    print(dico_triangles)
    for vert_ind, _ in enumerate(model_vertices):
        normale_totale = (0, 0, 0)
        for ind_triangle in dico_triangles[vert_ind]:
            v1 = np.array(model_vertices[model_faces[ind_triangle][0]])
            v2 = np.array(model_vertices[model_faces[ind_triangle][1]])
            v3 = np.array(model_vertices[model_faces[ind_triangle][2]])
            normale_courante = np.cross(v1-v2, v1-v3)
            normale_totale = normale_totale + normale_courante
        normale_totale = normale_totale/np.linalg.norm(normale_totale)
        liste.append(normale_totale)
    return liste

def middlebury(modelr_vertices, modelr_faces, modelg_vertices, modelg_faces, taux_acc=0.9, dist_comp=1.5):
    """
    Calcul de l'accuracy et de la completness d'un modele reconstruit (R) par rapport à
    un modèle de vérité terrain (G).
    `modelg` et `modelr` sont des obja.Model et représentent respectivement le modèle de la vérité
    terrain et le modèle à tester (dit modèle reconstruit)
    Le `taux_acc` permet de definir quel pourcentage de distances doivent être gardées pour
    évaluer le seuil qui permettent de les selectionner, qui est l'accuracy de R.
    La `dist_comp` permet de definir la distance seuil à garder pour évaluer le taux de distances
    placées à une distance inférieure à ce seuil, c'est le completeness de R.
    """
    # Calcul des normales :
    print(modelg_faces)
    if modelg_faces:
        ng = liste_normales(modelg_vertices, modelg_faces, liste_tri_points(modelg_faces))

        # Calcul de l'accuracy
        dist_acc = middlebury_accuracy(modelg_vertices, modelr_vertices, ng, taux_acc)

        # Calcul de la completeness
        taux_comp = middlebury_completeness(modelg_vertices, modelr_vertices, dist_comp)

    else:
        dist_acc = 0
        taux_comp = 0

    return (dist_acc, taux_comp)

def middlebury_accuracy(modelg_vertices, modelr_vertices, ng, taux_acc=0.9):
    """
    Pour calculer l'accuracy, on évalue la distance signée pour tous les vertex du modèle R
    avec le point le plus proche de G associé.
    `modelg` et `modelr` sont des obja.Model et représentent respectivement le modèle de la vérité
    terrain et le modèle à tester (dit modèle reconstruit)
    `ng` est la liste des normales associées à chaque vertex du modèle.
    """
    if (taux_acc > 1 or taux_acc <= 0):
        raise Exception("Taux invalide")
    
    verticesr = modelr_vertices
    verticesg = modelg_vertices
    res = distance.cdist(verticesr, verticesg, 'euclidean')
    distances = np.amin(res, axis=1)

    # Trouver la distance seuil qui garde `taux_acc` valeurs
    distances_tri = sorted(list(map(abs, distances)))
    index_dist = math.ceil(len(distances_tri)*taux_acc)-1
    dist_acc = distances_tri[index_dist]

    return dist_acc

def middlebury_completeness(modelg_vertices, modelr_vertices, dist_comp=1.5):
    """
    Pour calculer la complétude, on évalue la distance pour tous les vertex du modèle G
    avec le point le plus proche de R associé et si cette distance est inférieur à une
    distance dist_acc, on consière que le point de G est bien représenté par le modèle R, 
    la complétude est la proportion de points de G bien représentés par R.
    """
    verticesr = modelr_vertices
    verticesg = modelg_vertices
    res = distance.cdist(verticesg, verticesr, 'euclidean')
    distances = np.amin(res, axis=1)

    nb_valid = np.count_nonzero(distances < dist_comp)
    taux_comp = nb_valid/len(verticesg)
    return taux_comp