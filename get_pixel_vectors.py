import numpy as np
from skimage.draw import polygon
from scipy.spatial import ConvexHull


def get_pixel_vectors(vertices:list[tuple[int, int]], focal_distance:list[tuple[float, float]], optical_center:list[tuple[float, float]], img_size:tuple[int, int]) -> np.ndarray:
    unit_vectors = np.empty((img_size[0], img_size[1], 3), dtype=np.float32)

    np_vertices = np.array(vertices)
    hull = ConvexHull(np_vertices)
    np_vertices = np_vertices[hull.vertices]

    max_y = np_vertices[:, 0].max()
    max_x = np_vertices[:, 1].max()


    # Obtenemos los índices de los píxeles dentro del cuadrilátero
    rr, cc = polygon(np_vertices[:, 0], np_vertices[:, 1], (max_y + 1, max_x + 1))

    center_y = optical_center[0]
    center_x = optical_center[1]

    # Llenamos los puntos dentro del cuadrilátero con sus vectores unitarios
    fx = focal_distance[0]
    fy = focal_distance[1]
    for y, x in zip(rr, cc):
        vector = np.array([-(y - center_y) / (fy) , (x - center_x) / (fx), 1])
        unit_vector = vector #/ np.linalg.norm(vector)
        unit_vectors[y, x] = unit_vector

    return unit_vectors

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    vertices = [(5, 5), (5, 15), (15, 15), (15, 5)]
    focal_distance = 0.002
    img_size = (30,30)
    unit_vectors = get_pixel_vectors(vertices, focal_distance, img_size)
    print(unit_vectors)

    # graph unit vectors
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter([v[0] for v in unit_vectors], [v[1] for v in unit_vectors], [v[2] for v in unit_vectors])
    plt.show()
