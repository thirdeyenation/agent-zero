import cv2
import numpy as np

# Create a dummy image (replace with actual image loading later)
image = np.zeros((100, 100, 3), dtype=np.uint8)
image[:, :, 0] = 255  # Blue color

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Save the grayscale image
cv2.imwrite('/root/gray_image.png', gray_image)