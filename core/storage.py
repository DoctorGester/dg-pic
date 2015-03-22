import appdirs
import application
import requests
import shutil
import os
import wx

app_dir = appdirs.user_data_dir("dg-pic", False)
thumbnail_dir = os.path.join(app_dir, "thumbnails")
gallery_dir = os.path.join(app_dir, "gallery")

if not os.path.exists(thumbnail_dir):
    os.makedirs(thumbnail_dir, 0755)

if not os.path.exists(gallery_dir):
    os.makedirs(gallery_dir, 0755)


def store_thumbnail(name):
    full_url = application.AppFrame.MINI_URL.format(name)

    request = requests.get(full_url, stream=True)

    if request.status_code == 200:
        path = os.path.join(thumbnail_dir, name + ".png")

        with open(path, 'wb') as f:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, f)


def store_image(name, image):
    path = os.path.join(gallery_dir, name + ".png")
    image.ConvertToImage().SaveFile(path, wx.BITMAP_TYPE_PNG)


def is_image_stored(name):
    path = os.path.join(gallery_dir, name + ".png")
    return os.path.isfile(path)