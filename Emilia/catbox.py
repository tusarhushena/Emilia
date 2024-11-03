import os

from Emilia import telethn

from catbox import CatboxUploader
from Emilia.tele.telegraph import resize_image


uploader = CatboxUploader()


TMP_DOWNLOAD_DIRECTORY = "catbox/"


async def upload(img):
    downloaded_file_name = await telethn.download_media(img, TMP_DOWNLOAD_DIRECTORY)
    if downloaded_file_name.endswith((".webp")):
        resize_image(downloaded_file_name)
    try:
        media_urls = uploader.upload_file(downloaded_file_name)
    except:
        media_urls = uploader.upload_file(downloaded_file_name)
    os.remove(downloaded_file_name)
    return media_urls