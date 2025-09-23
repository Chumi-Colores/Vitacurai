import numpy as np
from math import sqrt

test_number = 3
data = np.load(f'outdir/test_{test_number}_raw_depth_meter.npy')


print(data.shape)

x = data.shape[1]//2
y_c = data.shape[0]//2

# estos valores los obtengo "manualmente" viendo la imagen
if test_number == 6:
    y_top = 618
    y_bottom = 1422
    depth_top = data[y_top,x]
    depth_c = data[y_c, x]
    depth_bottom = data[y_bottom,x]

    print("Depth Top", depth_top)
    print("Depth Center", depth_c)
    print("Depth Bottom", depth_bottom)

    h_top = sqrt(depth_top**2 - depth_c**2)
    h_bottom = sqrt(depth_bottom**2 - depth_c**2)
    height = (h_top + h_bottom)

    print("Height:", round(height, 2), "meters")
elif test_number == 3:
    y_top = 1561
    y_bottom = 2158
    depth_top = data[y_top,x]
    depth_c = data[y_c, x]
    depth_bottom = data[y_bottom,x]

    print("Depth Top", depth_top)
    print("Depth Center", depth_c)
    print("Depth Bottom", depth_bottom)

    h_top = sqrt(depth_top**2 - depth_c**2)
    h_bottom = sqrt(depth_bottom**2 - depth_c**2)
    height = (h_top + h_bottom)

    print("Height:", round(height, 2), "meters")
elif test_number == 2:
    x_left = 630
    x_right = 2825
    depth_left = data[y_c,x_left]
    depth_c = data[y_c, x]
    depth_right = data[y_c,x_right]

    print("Depth Left", depth_left)
    print("Depth Center", depth_c)
    print("Depth Right", depth_right)

    w_left = sqrt(depth_left**2 - depth_c**2)
    w_right = sqrt(depth_right**2 - depth_c**2)
    width = (w_left + w_right)

    print("Width:", round(width, 2), "meters")
