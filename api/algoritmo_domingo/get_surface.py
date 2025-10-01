import numpy as np

def get_surface(tridimensional_coordinates: np.ndarray):

    centroid = tridimensional_coordinates.mean(axis=0)
    points_centered = tridimensional_coordinates - centroid

    _, _, vh = np.linalg.svd(points_centered)

    normal_vector_to_surface = vh[-1]

    return (centroid, normal_vector_to_surface)
