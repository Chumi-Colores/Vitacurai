from flask import Flask, jsonify, request
import time
from get_pixel_vectors import get_pixel_vectors
from get_3D_coordinates import get_3D_coordinates
from get_surface import get_surface
from get_dimentions import get_dimentions

app = Flask(__name__)

@app.route('/publicity_size_calculator', methods=['POST'])
def publicity_size_calculator():
    data = request.get_json()
    image_link = data.get('image_link')
    vertices = data.get('vertices')
    focal_distance = data.get('focal_distance')
    image = data.get('image')  # en realidad esto lo obtenemos de image_link, lo dejo así por mientras para que vscode no se queje
    image_size = data.get('image_size') # en realidad esto lo calculamos nosotros, lo dejo así por mientras para que vscode no se queje
    
    # Flujo del algoritmo, solo falta recibir la información, averigua cómo se llaman los atributos que mandan
    vectors = get_pixel_vectors(vertices, focal_distance, image_size)
    tridimensional_coordinates = get_3D_coordinates(image, vectors, vertices)
    surface = get_surface(tridimensional_coordinates)
    width, height = get_dimentions(surface, tridimensional_coordinates)

    result = {
        "height": height,
        "width": width,
    }

    return jsonify(result)

@app.route('/calibration', methods=['POST'])
def calibration():
    # TODO: Implement calibration logic
    time.sleep(2)  # Simulate processing time
    return jsonify({"status": "calibration completed"})

if __name__ == '__main__':
    app.run()