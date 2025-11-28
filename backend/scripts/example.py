import cv2
import numpy as np
from PIL import Image

from app.lib import ContourVisualiser, HeatmapVisualiser, PixelComparer

# Load an image
img1 = Image.open("data/img1.jpg")
img2 = Image.open("data/img2.jpg")

# Convert the image to a NumPy array
img1_array = np.asarray(img1)
img2_array = np.asarray(img2)


# init comparer
cp = PixelComparer()

# init visualisaer
vis = ContourVisualiser()

# Load images
comparison = cp.compare(img1_array, img2_array)

map = np.array(comparison.gray_difference_map)

# result = np.where(map != 0)
# print(result)
# print(type(comparison.gray_difference_map))


result = vis.visualise(img1_array, img2_array, comparison)

cv2.imwrite("output.jpg", result.image)
