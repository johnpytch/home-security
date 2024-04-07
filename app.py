import os
from os import listdir
import sys
from PIL import Image
import time
from src.home_security.telegram import send_photo

sys.path.append("..")
from src.home_security.utils import get_datetime
from src.home_security.inference import inference
import json
from src.home_security.model import load_model
from src.home_security.annotations import annotate_detections
from collections import Counter

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


# initialise model
model, processor = load_model()


def inference_images(image_paths, household: str):

    # Specify who is receiving the image if there is a detection
    recipients = [
        USER_JOHN
    ]  # [USER_JOHN, USER_S] if household == DENN else [USER_JOHN, USER_A, USER_R]
    for image_path in image_paths:
        datetime = get_datetime(image_path)
        if (
            int(image_path.split("/")[4].split("_")[1].split(".")[0][8:10]) >= 20
            or int(int(image_path.split("/")[4].split("_")[1].split(".")[0][8:10])) <= 6
        ):  # decide score thresh depending on time of day
            min_det_score = 0.35  # nighttime
        else:
            min_det_score = 0.50  # daytime
        image = Image.open(image_path)

        start_time = time.time()
        detections = inference(model, processor, image, min_score=min_det_score)
        end_time = time.time()

        # Annotate image
        annotated_image = annotate_detections(image, detections)

        # Save inferenced image in respective inferenced folder
        inferenced_img_path = (
            INFERENCED_IMAGES_DENN if household == DENN else INFERENCED_IMAGES_REC
        )
        inferenced_img_path += image_path.split("/")[4]
        annotated_image.savefig(inferenced_img_path, bbox_inches="tight", pad_inches=0)

        # Save original image in respective old_images folder
        old_img_path = OLD_IMAGES_DENN if household == DENN else OLD_IMAGES_REC
        old_img_path += image_path.split("/")[4]
        image.save(old_img_path)  # save old image to new location
        os.remove(image_path)  # remove image from new images dir

        print(
            "Inferenced {} using score thresh {} in {}".format(
                image_path, min_det_score, str(end_time - start_time)
            )
        )

        # do something with detection
        if not detections:
            continue
        else:
            message = "Detected "

            # Get dict of the counts of unique items in the images detections
            unique_dets = {}
            for det in detections:
                if det["label"] not in unique_dets:
                    unique_dets[det["label"]] = 1
                else:
                    unique_dets[det["label"]] += 1
            unique_dets
            item_counts = dict(Counter(unique_dets))
            for key, value in item_counts.items():
                message = message + "{} {}, ".format(value, key)
            message = message.strip(", ")
            message = message + "\nAt {}".format(datetime)
            print(message)
            try:
                send_photo(
                    SEND_PHOTO_URL=SEND_PHOTO_URL,
                    image_path=inferenced_img_path,
                    image_caption=message,
                    recipients=recipients,
                )
            except:
                print("A telegram API connection occured. Retrying in 60s...")
                time.sleep(120)
                send_photo(
                    SEND_PHOTO_URL=SEND_PHOTO_URL,
                    image_path=inferenced_img_path,
                    image_caption=message + "\nHad connectivity issues before sending",
                    recipients=recipients,
                )
                pass


# Infinite inference loop
while True:

    image_paths_denning = [NEW_IMAGES_DENN + file for file in listdir(NEW_IMAGES_DENN)]
    image_paths_rectory = [NEW_IMAGES_REC + file for file in listdir(NEW_IMAGES_REC)]
    if image_paths_denning:
        inference_images(image_paths=image_paths_denning, household=DENN)
    if image_paths_rectory:
        inference_images(image_paths=image_paths_rectory, household=REC)
    time.sleep(30)
