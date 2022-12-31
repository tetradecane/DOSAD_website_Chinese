import os
from image_lib import *

for tmp_package_name in os.listdir(folder_screenshots):
    images = []
    for root, dirs, files in os.walk(os.path.join(folder_screenshots, tmp_package_name)):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)
            image = Image.open(file_path)
            image = resize_and_crop(image)
            images.append({'path': file_path, 'image': image})
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            if get_sim_of_2_images(images[i]['image'], images[j]['image']) == 1.0:
                print('{} {}'.format(i, images[i]['path']))
                os.remove(images[i]['path'])
                break
