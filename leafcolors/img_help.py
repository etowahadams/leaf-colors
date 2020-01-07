import cv2
import numpy as np


def remove_dark(img):
    """
    Removes pixels which has a 0 value in any color channel
    :param img: <class 'numpy.ndarray'>
    :rtype: <class 'numpy.ndarray'> - numpy float 32 array
    """
    img_arr = img.tolist()

    for i, row in enumerate(img_arr):
        img_arr[i] = list(filter(lambda x: np.all(x), row))

    img_list = list(filter(lambda x: x != [], img_arr))
    img_list = [tuple for row in img_list for tuple in row]
    pixels = np.float32(img_list)
    return pixels


def dom_color(img, n_colors):
    """
    Finds the dominant color of an image, using k means. n_colors = k
    :param n_colors: int
    :param img: <class 'numpy.ndarray'>
    :rtype: [B, G, R]
    """
    # adapted from Tonechas https://stackoverflow.com/a/43111221
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    noDark = remove_dark(img)
    if noDark.size > 2:
        img = noDark
    else:
        img = np.float32(img)
    _, labels, palette = cv2.kmeans(img, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    dominant = palette[np.argmax(counts)]
    """
    height, width, channels = img.shape
    dom_color_bgr = np.full((height, width, channels), dominant, dtype='uint8')
    column = cv2.vconcat([img, dom_color_bgr])
    cv2.imshow("grabbed", column)
    cv2.waitKey(0)
    """
    return dominant


def grab_cut(img):
    """
    Takes an image and returns the cropped image using grabcut
    :param img: <class 'numpy.ndarray'>
    :rtype: <class 'numpy.ndarray'>
    """
    # adapted from OpenCV docs https://docs.opencv.org/3.4/d8/d83/tutorial_py_grabcut.html
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    height, width = img.shape[:2]
    rect = (1, 1, width - 2, height - 2)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    grabbedImg = img * mask2[:, :, np.newaxis]
    # cv2.imshow("grabbed", grabbedImg)
    # cv2.waitKey(0)
    if cv2.countNonZero(cv2.cvtColor(grabbedImg, cv2.COLOR_BGR2GRAY)) == 0:
        # if grabbedImg is completely black, i.e. cv2.grabCut removed everything, return original img
        print('all black img')
        return img
    return grabbedImg


def hconcat_resize(img_list):
    """
    Takes a list of images and returns an image of the horizontally concatenated list of images, resized to the
    minimum height of the list of images
    :param im_list list of <class 'numpy.ndarray'>
    :rtype: <class 'numpy.ndarray'>
    """
    min_height = min(img.shape[0] for img in img_list)
    img_list_resize = [cv2.resize(img, (int(img.shape[1] * min_height / img.shape[0]), min_height), cv2.INTER_CUBIC)
                       for img in img_list]
    return cv2.hconcat(img_list_resize)


def crop_img(img, leaf):
    """
    For a given image and leaf position, returns the img, cropped to the leaf
    :param img: image that needs to be cropped
    :param leaf: {'x': int, 'y': int, 'width': int, 'height': int}
    :return: cropped image
    """
    height = leaf['height']
    width = leaf['width']
    x = leaf['x']
    y = leaf['y']
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    cropped = img[y:y + height, x:x + width]
    # cv2.imshow("cropped", cropped)
    # cv2.waitKey(0)
    return cropped


def get_color(img, leaf):
    """
    For a given image and leaf information, return the color of the leaf in the image
    :param img: <nparray>
    :param leaf: dict containing height, width, x, and y
    :return: <nparray> [B, G, R]
    """
    cropped = crop_img(img, leaf)
    grabbedImg = grab_cut(cropped)

    k = 2  # for k-means
    color = dom_color(grabbedImg, k)
    return color
