import requests
from typing import List


def send_photo(SEND_PHOTO_URL, image_path, image_caption, recipients: List):
    for recipient in recipients:
        data = {"chat_id": recipient, "caption": image_caption}
        with open(image_path, "rb") as img:
            requests.post(SEND_PHOTO_URL, data=data, files={"photo": img})
    return True
