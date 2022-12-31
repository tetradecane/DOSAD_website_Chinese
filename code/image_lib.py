from params import *
from PIL import Image
from PIL import ImageChops
import numpy as np


def get_sim_of_2_images(image_1, image_2):
    """
    :param image_1: file name str or Image object.
    :param image_2: file name str or Image object.
    :return: 1.00 means all pixels the same; 0.00 means all pixels different.
    """
    if type(image_1) == str:
        image_1 = Image.open(image_1)
    if type(image_2) == str:
        image_2 = Image.open(image_2)

    image_sub = ImageChops.subtract_modulo(image_1, image_2)

    num_all_pixel = image_sub.size[0] * image_sub.size[1]
    num_black_pixel = 0
    for r in range(image_sub.size[0]):
        for c in range(image_sub.size[1]):
            if image_sub.getpixel((r, c)) == (0, 0, 0):
                num_black_pixel += 1
    return round(num_black_pixel / num_all_pixel, 4)


def pearson(image1, image2):
    """
    :param image1: str of file name or Image object.
    :param image2: str of file name or Image object.
    :return: float number in [0.00, 1.00], higher means more similar.
    """
    if type(image1) == str:
        image1 = Image.open(image1)
    if type(image2) == str:
        image2 = Image.open(image2)
    image1 = resize_and_crop(image1)
    image2 = resize_and_crop(image2)
    image1 = np.asarray(image1).ravel()
    image2 = np.asarray(image2).ravel()
    X = np.vstack([image1, image2])
    return np.corrcoef(X)[0][1]


def resize_and_crop(image, target_size=target_size_best, resample_filter=Image.LANCZOS):
    """
    :param image: str of file name or Image object.
    :param target_size: size after resizing.
    :param resample_filter: resample filter.
    :return: a Image object, after resizing and cropping.
    """
    if type(image) == str:
        image = Image.open(image)
    image = image.convert(mode="RGB")
    image = image.resize(size=target_size, resample=resample_filter)
    # crop the status bar and navigation buttons
    crop_len = list(map(lambda x: int(np.ceil(x * target_size[1])), crop_ratio))
    crop_rect = (0, crop_len[0], target_size[0], target_size[1] - crop_len[1])
    result = image.crop(crop_rect)
    return result


if __name__ == "__main__":
    # noinspection PyTypeChecker
    print(pearson("1.png", "2.png"))
