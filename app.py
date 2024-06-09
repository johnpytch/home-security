import os
from os import listdir
import sys
from PIL import Image
from typing import List
import time
import logging
import json
from collections import Counter
from src.home_security.telegram import send_photo
from src.home_security.utils import get_datetime
from src.home_security.inference import inference

from src.home_security.model import load_model
from src.home_security.annotations import annotate_detections

sys.path.append("..")
# Configure the logging settings
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Load env json
with open("./env.json", "r") as file:
    env_json = json.load(file)

env_tokens = env_json.get("TOKENS")
env_households = env_json.get("HOUSEHOLDS")
env_urls = env_json.get("URLS")

# Get bot and user IDs for telegram
BOT_TOKEN = env_tokens.get("BOT_TOKEN")
USER_JOHN = env_tokens.get("USER_JOHN")
USER_S = env_tokens.get("USER_S")
USER_R = env_tokens.get("USER_R")
USER_A = env_tokens.get("USER_A")


# Base household foldernames for image directories
DENN = env_households.get("DENN")
REC = env_households.get("REC")

# Full housefold folder paths for image directories
NEW_IMAGES_DENN = f"./images/new_images/{DENN}/"
NEW_IMAGES_REC = f"./images/new_images/{REC}/"
OLD_IMAGES_DENN = f"./images/old_images/{DENN}/"
OLD_IMAGES_REC = f"./images/old_images/{REC}/"
INFERENCED_IMAGES_DENN = f"./images//inferenced/{DENN}/"
INFERENCED_IMAGES_REC = f"./images/inferenced/{REC}/"

# URLs for telegram bot posts
SEND_MSG_URL = env_urls.get("SEND_MSG_URL").format(TOKEN=BOT_TOKEN)
SEND_PHOTO_URL = env_urls.get("SEND_PHOTO_URL").format(TOKEN=BOT_TOKEN)

logging.info(f"Environment initialised for {DENN} and {REC}")

# initialise model
model, processor = load_model()


def inference_images(image_paths: List[str], household: str):

    # Specify who is receiving the image if there is a detection.
    recipients = [
        USER_JOHN
    ]  # [USER_JOHN, USER_S] if household == DENN else [USER_JOHN, USER_A, USER_R]
    for image_path in image_paths:
        datetime = get_datetime(image_path=image_path)

        # Decide score thresh depending on hour of day
        # TODO: Use proper datetime type
        if int(datetime[0:2]) >= 21 or int(datetime[0:2]) <= 6:
            min_det_score = 0.60
        else:
            min_det_score = 0.70

        # Inference image
        image = Image.open(image_path)
        start_time = time.time()
        detections = inference(
            model=model, processor=processor, image=image, min_score=min_det_score
        )
        end_time = time.time()

        # Annotate image
        annotated_image = annotate_detections(image=image, detections=detections)

        # Save inferenced image in respective inferenced folder
        inferenced_img_path = (
            INFERENCED_IMAGES_DENN if household == DENN else INFERENCED_IMAGES_REC
        )
        inferenced_img_path += image_path.split("/")[4]
        annotated_image.save(inferenced_img_path)

        # Save original image in respective old_images folder
        old_img_path = OLD_IMAGES_DENN if household == DENN else OLD_IMAGES_REC
        old_img_path += image_path.split("/")[4]
        image.save(old_img_path)  # save old image to new location
        os.remove(image_path)  # remove image from new images dir

        logging.info(
            f"Inferenced image_path {image_path} using score thresh {min_det_score} in {end_time - start_time}"
        )

        # Do something with detection
        if detections:
            message = "Detected "

            # Get dict of the counts of unique items in the images detections
            unique_dets = {}
            for det in detections:
                if det["label"] not in unique_dets:
                    unique_dets[det["label"]] = 1
                else:
                    unique_dets[det["label"]] += 1

            # Add detections to a message
            item_counts = dict(Counter(unique_dets))
            for key, value in item_counts.items():
                if value > 1:
                    class_name = "people"
                else:
                    class_name = key
                message = message + f"{value} {class_name},"
            message = message.strip(", ")
            message = message + " at {}".format(datetime)
            logging.info(message)

            # Send message to recipients, retrying if there are any connectivity issues
            sent = False
            while not sent:
                try:
                    send_photo(
                        SEND_PHOTO_URL=SEND_PHOTO_URL,
                        image_path=inferenced_img_path,
                        image_caption=message,
                        recipients=recipients,
                    )
                    sent = True
                except:
                    logging.warning(
                        "A telegram API connection occured. Retrying in 120s..."
                    )
                    time.sleep(120)


# Infinite inference loop
while True:

    image_paths_denning = [NEW_IMAGES_DENN + file for file in listdir(NEW_IMAGES_DENN)]
    image_paths_rectory = [NEW_IMAGES_REC + file for file in listdir(NEW_IMAGES_REC)]
    if image_paths_denning:
        inference_images(image_paths=image_paths_denning, household=DENN)
    if image_paths_rectory:
        inference_images(image_paths=image_paths_rectory, household=REC)
    time.sleep(30)
