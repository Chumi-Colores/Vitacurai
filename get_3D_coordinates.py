from metric_depth import depth_predictor
import numpy as np
from skimage.draw import polygon
from scipy.spatial import ConvexHull

# Esta función toma una imagen, un mapa de profundidad y una lista de vectores unitarios
# y devuelve las coordenadas 3D correspondientes a los píxeles dentro del cuadrilátero
def get_3D_coordinates(image, unit_vectors: np.ndarray, vertices:list[tuple[int, int]]) -> np.ndarray:
    depth_map = depth_predictor.predict_depth(image)

    np_vertices = np.array(vertices)
    hull = ConvexHull(np_vertices)
    np_vertices = np_vertices[hull.vertices]

    max_y = np_vertices[:, 0].max()
    max_x = np_vertices[:, 1].max()

    # Obtenemos los índices de los píxeles dentro del cuadrilátero
    rr, cc = polygon(np_vertices[:, 0], np_vertices[:, 1], (max_y + 1, max_x + 1))

    print("Starting depth projection...")
    # Calculamos las coordenadas 3D para cada píxel dentro del cuadrilátero
    depths = depth_map[rr, cc]                  # shape (N,)
    unit_vecs = unit_vectors[rr, cc]            # shape (N, 3)

    # Multiplicamos por broadcasting
    tridimensional_coordinates = unit_vecs * depths[:, np.newaxis]  

    print(tridimensional_coordinates.shape)

    return tridimensional_coordinates

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from PIL import Image

    image = np.array(Image.open("0. PUBLICIDAD\\COSTANERA NORTE 4700\\TimePhoto_20220107_112830.jpg"))
    vertices = [(1250, 629), (1661, 626), (1668, 2834), (1244, 2833)]
    focal_distance = 4.4 # en milímetros
    img_size = (image.shape[0], image.shape[1])
    from get_pixel_vectors import get_pixel_vectors
    unit_vectors = get_pixel_vectors(vertices, focal_distance, img_size)
    tridimensional_coordinates = get_3D_coordinates(image, unit_vectors, vertices)

    # graph tridimensional coordinates
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    N = tridimensional_coordinates.shape[0]

    # índice aleatorio para tomar solo el 25%
    num_sample = N // 32
    sample_idx = np.random.choice(N, num_sample, replace=False)

    # seleccionamos los puntos muestreados
    sampled_coords = tridimensional_coordinates[sample_idx]

    # separamos las coordenadas
    ys = sampled_coords[:, 0]
    minimum_y = ys.min()
    maximum_y = ys.max()
    print(f"Y min: {minimum_y}, Y max: {maximum_y}")

    xs = sampled_coords[:, 1]
    maximum_x = xs.max()
    minimum_x = xs.min()
    print(f"X min: {minimum_x}, X max: {maximum_x}")

    zs = sampled_coords[:, 2]
    maximum_z = zs.max()
    minimum_z = zs.min()
    print(f"Z min: {minimum_z}, Z max: {maximum_z}")

    ax.scatter(xs, zs, ys)

    ax.set_xlim(-max(abs(minimum_x), abs(maximum_x))-1, max(abs(minimum_x), abs(maximum_x))+1)
    ax.set_zlim(-max(abs(minimum_y), abs(maximum_y))-1, max(abs(minimum_y), abs(maximum_y))+1)
    ax.set_ylim(0, max(abs(minimum_z), abs(maximum_z))+1)
    plt.show()