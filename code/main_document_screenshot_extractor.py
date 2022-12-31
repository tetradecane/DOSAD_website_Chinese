import io

from selenium import webdriver
import requests
import os
from PIL import Image

from params import *

if __name__ == '__main__':
    print()
    print('Document URL: {}'.format(document_url))
    print('APK package name: {}'.format(package_name))

    op = webdriver.ChromeOptions()
    op.add_argument('lang=en-US')
    driver = webdriver.Chrome(options=op)
    driver.get(document_url)
    driver.find_element_by_xpath('//button[@data-screenshot-item-index="0"]').click()
    imgs_screenshot = driver.find_elements_by_xpath('//div[@data-expanded-slideshow-item-index]/img')

    save_dir = os.path.join(folder_screenshots, package_name, '0')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print('Downloading... ')
    num_kept = 0
    for img in imgs_screenshot:
        src = img.get_attribute('src')
        response = requests.get(src)

        image = Image.open(io.BytesIO(response.content))
        w, h = image.size
        if w / h > 9 / 16 + 0.05 or w / h < 9 / 16 - 0.05:
            print('1 screenshot deleted.')
        else:
            with open(os.path.join(save_dir, '{}.png'.format(num_kept)), 'wb') as f:
                f.write(response.content)
                print('{}/{} screenshots downloaded.'.format(num_kept + 1, len(imgs_screenshot)))
            num_kept += 1

    print('Num kept: {}'.format(num_kept))
    driver.close()
