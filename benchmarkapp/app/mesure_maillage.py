import obja
import math
import numpy as np


def haussdorf_naif(model1, model2):
    """
    Calcule la distance de Haussdorf relative des sommets du modèle 1 vers les sommets
    du modèle 2. C'est à dire le max des distances minimales des sommets de 1 aux sommets de 2.
    Version naive, qui utilise seulement les sommets
    """
    vertices1 = model1.vertices
    vertices2 = model2.vertices
    d1_max = -math.inf
    for vertexR in vertices1:
        d2_min = math.inf
        for vertexG in vertices2:
            d = dist(vertexR.x, vertexR.y, vertexR.z, vertexG.x, vertexG.y, vertexG.z)
            if d < d2_min:
                d2_min = d

        if d2_min > d1_max:
            d1_max = d2_min

    return d1_max


def cross(v1, v2):
    """
    Calcule le produit vectoriel entre v1 et v2
    v1 et v2 sont des obja.Vector
    """
    x = v1.y * v2.z - v1.z * v2.y
    y = v1.z * v2.x - v1.x * v2.z
    z = v1.x * v2.y - v1.y * v2.x
    return obja.Vector(x, y, z)


def dot(v1, v2):
    """
    Calcule le produit scalaire entre v1 et v2
    v1 et v2 sont des obja.Vector
    """
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z


def norm(vect):
    """
    Calcule la norme du vecteur vect
    vect est un obja.Vector
    """
    return math.sqrt(vect.x ** 2 + vect.y ** 2 + vect.z ** 2)


def dist(x1, y1, z1, x2, y2, z2):
    """
    Calcule la distance euclidienne entre un point 1 de coordonées (x1, y1, z1)
    et un point 2 de coordonées (x2, y2, z2)
    """
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


# Les vertex de 1 par rapport aux faces de 2
def haussdorf_dist_triangle(model1, model2, isPrinting=False):
    """
    On calcule la distance de Haussdorf du modèle 1 au modèle 2 en trouvant
    la distance entre tous les vertex de 1 et chaque triangles de 2.
    """
    vertices1 = model1.vertices
    faces2 = model2.faces

    liste_dist_min = [math.inf for _ in vertices1]

    if isPrinting:
        stri = "\rhaussdorf_dist_triangle {:5.1f}% terminé".format(0)
        print(stri, end="")

    i = 0
    for face in faces2:
        i += 1
        v1 = model2.vertices[face.a]
        v2 = model2.vertices[face.b]
        v3 = model2.vertices[face.c]
        res = algo(vertices1, (v1, v2, v3))

        if isPrinting & (i % 100 == 0):
            prog = i / len(faces2) * 100
            stri = "\rhaussdorf_dist_triangle {:5.1f}% terminé".format(prog)
            print(stri, end="")

        # assert(len(res) == len(liste_dist_min))

        for ind, val in enumerate(res):
            if val < liste_dist_min[ind]:
                liste_dist_min[ind] = val

    if isPrinting:
        print("")

    return np.max(liste_dist_min)


def algo(vertices1, vertices_tri2):
    """
    Algorithme qui calcul la distance entre tous les points de vertices 1 et le triangle de vertices_tri2
    vertices1 est une liste de obja.Vertex
    vertices_tri2 est un tuple de obja.Vertex representant les vertex du triangle.
    Retourne la liste des distances où pour chaque vertex de vertices1, on donne la distance au triangle.
    """

    # Calcul des equations du plan, la normale, etc...
    # vertices_tri2 est un tuple avec chaque vertex du triangle
    vt1 = vertices_tri2[0]
    vt2 = vertices_tri2[1]
    vt3 = vertices_tri2[2]

    # La normale au plan du triangle
    normale = cross(vt1.__sub__(vt2), vt1.__sub__(vt3))
    norme_normale = norm(normale)
    aire_tri = norme_normale / 2
    normale = normale / norme_normale

    # Calcul de a, b, c, d parametres du plan associé au triangle
    # a, b, c sont les coordonées du vecteur normale
    # d est un point appartenant au plan
    a = normale.x
    b = normale.y
    c = normale.z
    d = -(a * vt1.x + b * vt1.y + c * vt1.z)

    liste_dist_min = []

    for vertexR in vertices1:
        # Projection du vertex dans le plan du triangle avec x, y, z les coord d'un point à projeter
        # cf [https://fr.wikipedia.org/wiki/Projection_affine#Expression_analytique]
        # x' = ((b**2 + c**2)*x - a*b*y - a*c*z - d*a)/(a**2 + b**2 + c**2)
        # y' = (-a*b*x + (a**2 + c**2)*y - b*c*z - d*b)/(a**2 + b**2 + c**2)
        # z' = (-a*c*x - b*c*y + (a**2 + b**2)*z - d*c)/(a**2 + b**2 + c**2)
        vpx = ((b ** 2 + c ** 2) * vertexR.x - a * b * vertexR.y - a * c * vertexR.z - d * a) / (
                    a ** 2 + b ** 2 + c ** 2)
        vpy = (-a * b * vertexR.x + (a ** 2 + c ** 2) * vertexR.y - b * c * vertexR.z - d * b) / (
                    a ** 2 + b ** 2 + c ** 2)
        vpz = (-a * c * vertexR.x - b * c * vertexR.y + (a ** 2 + b ** 2) * vertexR.z - d * c) / (
                    a ** 2 + b ** 2 + c ** 2)

        # P.x, P.y, P.z
        P = obja.Vector(vpx, vpy, vpz)

        # Calcul des différentes normales des sous triangles
        normaleABP = cross(vt1.__sub__(vt2), vt1.__sub__(P))
        normaleBCP = cross(vt2.__sub__(vt3), vt2.__sub__(P))
        normaleCAP = cross(vt3.__sub__(vt1), vt3.__sub__(P))

        # Direction des normales
        if (normale.z != 0.0):
            directionABP = (normaleABP.z / normale.z)
            directionBCP = (normaleBCP.z / normale.z)
            directionCAP = (normaleCAP.z / normale.z)
        elif (normale.y != 0.0):
            directionABP = (normaleABP.y / normale.y)
            directionBCP = (normaleBCP.y / normale.y)
            directionCAP = (normaleCAP.y / normale.y)
        elif (normale.x != 0.0):
            directionABP = (normaleABP.x / normale.x)
            directionBCP = (normaleBCP.x / normale.x)
            directionCAP = (normaleCAP.x / normale.x)
        else:
            raise Exception("La normale va mal (le triangle est un petit peu comprimé sur lui-même)")

        # Obtenir des aires algébriques (remises à zéro si négatives (la normale est orientée dans l'autre sens))
        # La remise à zéro permet de prendre un point du bord du triangle
        if (directionABP <= 0):
            aireABP = 0
        else:
            aireABP = norm(normaleABP) / 2

        if (directionBCP <= 0):
            aireBCP = 0
        else:
            aireBCP = norm(normaleBCP) / 2

        if (directionCAP <= 0):
            aireCAP = 0
        else:
            aireCAP = norm(normaleCAP) / 2

        aire = aireABP + aireBCP + aireCAP
        # Coordonnées barycentriques
        coeffABP = aireABP / aire
        coeffBCP = aireBCP / aire
        coeffCAP = aireCAP / aire

        # Le point D le plus proche du projeté P dans le triangle ABC
        D = vt1.__mul__(coeffBCP).__add__(vt2.__mul__(coeffCAP)).__add__(vt3.__mul__(coeffABP))

        # On calcule la distance du point au triangle
        dist = norm(D.__sub__(vertexR))

        # On ajoute la distance trouvée à la liste des distances
        liste_dist_min.append(dist)

    return liste_dist_min


### Middlebury
# Obtenir la liste des triangles associés à un point
def liste_tri_points(model):
    """
    Produit un dictionnaire qui contient la liste de indices des triangles associés à chaque points du model.
    """
    dico = {}
    for ind, face in enumerate(model.faces):
        if face.a in dico:
            dico[face.a].append(ind)
        else:
            dico[face.a] = [ind]

        if face.b in dico:
            dico[face.b].append(ind)
        else:
            dico[face.b] = [ind]

        if face.c in dico:
            dico[face.c].append(ind)
        else:
            dico[face.c] = [ind]

    return dico


# Obtenir la normale associée à chaque points
def liste_normales(model, dico_triangles):
    """
    Produit la liste des normales associées à chaque points du model
    Il faut d'abord avoir calculé la liste des triangles associés à chaque points avec `liste_tri_points(model)`
    et le passer dans l'argument `dico_triangles`
    """
    liste = []
    for vert_ind, vertex in enumerate(model.vertices):
        normale_totale = obja.Vector(0, 0, 0)
        for ind_triangle in dico_triangles[vert_ind]:
            v1 = model.vertices[model.faces[ind_triangle].a]
            v2 = model.vertices[model.faces[ind_triangle].b]
            v3 = model.vertices[model.faces[ind_triangle].c]
            normale_courante = cross(v1.__sub__(v2), v1.__sub__(v3))
            normale_totale = normale_totale.__add__(normale_courante)
        normale_totale = normale_totale.__truediv__(norm(normale_totale))
        liste.append(normale_totale)
    return liste


def middlebury(modelg, modelr, taux_acc=0.9, dist_comp=1.5):
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
    ng = liste_normales(modelg, liste_tri_points(modelg))
    # nr = liste_normales(modelr, liste_tri_points(modelr))

    # Calcul de l'accuracy
    dist_acc = middlebury_accuracy(modelg, modelr, ng, taux_acc)

    # Calcul de la completeness
    taux_comp = middlebury_completeness(modelg, modelr, dist_acc)

    return (dist_acc, taux_comp)


def middlebury_accuracy(modelg, modelr, ng, taux_acc=0.9):
    """
    Pour calculer l'accuracy, on évalue la distance signée pour tous les vertex du modèle R
    avec le point le plus proche de G associé.
    `modelg` et `modelr` sont des obja.Model et représentent respectivement le modèle de la vérité
    terrain et le modèle à tester (dit modèle reconstruit)
    `ng` est la liste des normales associées à chaque vertex du modèle.
    """
    if (taux_acc > 1 or taux_acc <= 0):
        raise Exception("Taux invalide")

    verticesr = modelr.vertices
    verticesg = modelg.vertices
    distances = []
    for vertexR in verticesr:
        d2_min = math.inf
        for indG, vertexG in enumerate(verticesg):
            signe = dot(ng[indG], vertexR.__sub__(vertexG))
            d = dist(vertexR.x, vertexR.y, vertexR.z, vertexG.x, vertexG.y, vertexG.z)
            if (signe < 0.0):
                d = -d
            if abs(d) < abs(d2_min):
                d2_min = d
        distances.append(d2_min)

    # Trouver la distance seuil qui garde `taux_acc` valeurs
    distances_tri = sorted(list(map(abs, distances)))
    index_dist = math.ceil(len(distances_tri) * taux_acc) - 1
    dist_acc = distances_tri[index_dist]

    return dist_acc


def middlebury_completeness(modelg, modelr, dist_acc=1.5):
    """
    Pour calculer la complétude, on évalue la distance pour tous les vertex du modèle G
    avec le point le plus proche de R associé et si cette distance est inférieur à une
    distance dist_acc, on consière que le point de G est bien représenté par le modèle R, 
    la complétude est la proportion de points de G bien représentés par R.
    """
    verticesr = modelr.vertices
    verticesg = modelg.vertices
    nb_valid = 0
    nb = 0
    # Pour tous les sommets de G on calcule la distance minimale à un sommet de R
    for vertexG in verticesg:
        d2_min = math.inf
        for vertexR in verticesr:
            d = dist(vertexR.x, vertexR.y, vertexR.z, vertexG.x, vertexG.y, vertexG.z)
            if d < d2_min:
                d2_min = d
        nb += 1
        # Et on valide l'association si la distance trouvé est assez faible
        if (d2_min < dist_acc):
            nb_valid += 1
    taux_comp = nb_valid / nb
    return taux_comp
