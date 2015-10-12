import appdirs
import requests
import shutil
import os
import wx

app_dir = appdirs.user_data_dir("dg-pic", False)
thumbnail_dir = os.path.join(app_dir, "thumbnails")

if not os.path.exists(thumbnail_dir):
    os.makedirs(thumbnail_dir, 0755)


def get_gallery_dir(config):
    result = config.gallery_dir
    if result is None:
        result = os.path.join(app_dir, "gallery")

    if not os.path.exists(result):
        os.makedirs(result, 0755)

    return result


def store_thumbnail(mini_url, name):
    full_url = mini_url.format(name)

    request = requests.get(full_url, stream=True)

    if request.status_code == 200:
        path = os.path.join(thumbnail_dir, name + ".png")

        with open(path, 'wb') as f:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, f)


def store_image(config, name, image):
    path = os.path.join(get_gallery_dir(config), name + ".png")
    image.ConvertToImage().SaveFile(path, wx.BITMAP_TYPE_PNG)


def is_image_stored(config, name):
    path = os.path.join(get_gallery_dir(config), name + ".png")
    return os.path.isfile(path)