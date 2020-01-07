import cv2
import numpy as np
import glob
from leafcolors import img_help as ih

# grabcutgraphic.py
# Generates an image of the process that an image goes through find the color of a leaf

folder = glob.glob("cropped/*.jpg")  # folder containing images of leaves

rows = []
for crop in folder:
    img = cv2.imread(crop)

    grabbed_img = ih.grab_cut(img)
    column = cv2.vconcat([img, grabbed_img])

    k = 2  # for k-means
    grabbed_color = ih.dom_color(grabbed_img, k)
    height, width, channels = img.shape
    dom_color_bgr = np.full((height, width, channels), grabbed_color, dtype='uint8')
    column = cv2.vconcat([column, dom_color_bgr])

    rows.append(column)
    # cv2.imwrite('grabby/prog' + crop[8:], grabbed_img)

im_h_resize = ih.hconcat_resize(rows)
cv2.imshow('img', im_h_resize)  # Display
cv2.waitKey()
# cv2.imwrite('total.jpg', im_h_resize)
