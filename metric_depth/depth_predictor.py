import cv2
import torch
import time

from metric_depth.depth_anything_v2.dpt import DepthAnythingV2


encoder = "vitl"
features = 256
out_channels = [256, 512, 1024, 1024]
max_depth_in_meters = 80
weight_load_from = "checkpoints/depth_anything_v2_metric_vkitti_vitl.pth"
input_size = 518

DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'

depth_anything = DepthAnythingV2(encoder=encoder, features=features, out_channels=out_channels, max_depth=max_depth_in_meters)
depth_anything.load_state_dict(torch.load(weight_load_from, map_location='cpu'))
depth_anything = depth_anything.to(DEVICE).eval()

def predict_depth(raw_image):
    depth_matrix_in_meters = depth_anything.infer_image(raw_image, input_size)
    print("prediction done")

    return depth_matrix_in_meters


if __name__ == "__main__":
    img_path = "test_2.jpg"
    raw_image = cv2.imread(img_path)
    predict_depth(raw_image)
    start_time = time.time()
    predict_depth(raw_image)
    end_time = time.time()
    print(f"Time taken for second prediction: {end_time - start_time} seconds")