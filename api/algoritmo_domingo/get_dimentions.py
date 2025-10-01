import numpy as np

def get_dimentions(surface, vertices):
    centroid, normal_vector = surface
    np_vertices = np.array(vertices)

    # Proyectar los vértices sobre el plano definido por el centroide y el vector normal
    def project_point(point, plane_point, plane_normal):
        point_vector = point - plane_point
        distance = np.dot(point_vector, plane_normal)
        projected_point = point - distance * plane_normal
        return projected_point

    projected_vertices = np.array([project_point(v, centroid, normal_vector) for v in np_vertices])

    max_y = projected_vertices[:, 0].max()
    min_y = projected_vertices[:, 0].min()
    height = max_y - min_y

    max_x = projected_vertices[:, 1].max()
    min_x = projected_vertices[:, 1].min()
    width = max_x - min_x

    return width, height