import numpy as np
from scipy.spatial import distance

# Compute the Hausdorff metrics between two meshes
def hausdorff(original_model_vertices,compressed_model_vertices):
    euclidean_distances = distance.cdist(original_model_vertices,compressed_model_vertices, 'euclidean')
    distances = np.amin(euclidean_distances, axis=0)
    return np.amax(distances)