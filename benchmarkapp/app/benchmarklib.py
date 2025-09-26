from app import app
from scipy.spatial import distance
from app.obja import parse_file as ps_obja
from app.obj import parse_file as ps_obj
from app.metrics.hausdorff import hausdorff
from app.metrics.middleburry import middlebury
import math
import numpy as np
import os

OBJ_FILE = os.path.join(app.config['OBJ_FOLDER'], 'bunny.obj')
OBJA_FILE = 'bunny_prog.obj'
TODO = "TODO"


def getBbox(vert_list):
    minx = miny = minz = np.inf
    maxx = maxy = maxz = -np.inf
    for vertex in vert_list:
        if vertex[0] < minx:
            minx = vertex[0]
        elif vertex[0] > maxx:
            maxx = vertex[0]
        if vertex[1] < miny:
            miny = vertex[1]
        elif vertex[1] > maxy:
            maxy = vertex[1]
        if vertex[2] < minz:
            minz = vertex[2]
        elif vertex[2] > maxz:
            maxz = vertex[2]
    return minx, maxx, miny, maxy, minz, maxz


def getDiagonal(vert_list):
    (minx, maxx, miny, maxy, minz, maxz) = getBbox(vert_list)
    d = np.sqrt(np.power(maxx - minx, 2) + np.power(maxy - miny, 2) + np.power(maxz - minz, 2))
    return d


def obja_parser(obja_file):
    model = ps_obja(obja_file)
    steps, vertex_list, face_list, size, declared_size = model.steps, model.vertex_steps, model.faces_steps, model.size, model.declared_size
    return steps, vertex_list, face_list, size, declared_size


def obj_parser(obj_file):
    model = ps_obj(obj_file)
    vertex_list, face_list = model.get_lists()
    return vertex_list, face_list


def evaluate(input_obja, reference_file, dist_comp=app.config['DIST_COMP'], taux_acc=app.config['TAUX_ACC']):
    haus = []
    middle_acc = []
    middle_comp = []
    original_model_vert, original_model_faces = obj_parser(
        os.path.join(app.config['OBJ_FOLDER'], app.config['AVAILABLE_MODELS'][reference_file]['file']))
    steps, compressed_model_vert, compressed_model_faces, size, declared_size = obja_parser(input_obja)
    for vert_list, faces_list in zip(compressed_model_vert, compressed_model_faces):
        haus.append(hausdorff(vert_list, original_model_vert))
        res = middlebury(original_model_vert, original_model_faces, vert_list, faces_list, taux_acc=taux_acc,
                         dist_comp=dist_comp * getDiagonal(original_model_vert))
        middle_comp.append(res[1])
        middle_acc.append(res[0])
    return steps, haus, middle_acc, middle_comp, size, declared_size


def tab2text(tab):
    texttab = ""
    for elt in tab:
        texttab += str(elt) + " "
    return texttab[:-1]
