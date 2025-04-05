from PIL import Image
from typing import List
import time
import logging
import asyncio

from home_security.telegram import send_photo
from home_security.inference import inference
from home_security.model import load_model
from home_security.annotations import annotate_detections
from home_security.settings import settings
from home_security.data.minio.minio_client import Minio
from home_security.data.storage import StorageDriver
from home_security.data.postgresql.database import get_session, create_tables, seed_db
from home_security.data.postgresql.models import Detection

logging.basicConfig(level=logging.INFO)
logging.info(f"Environment initialised")

minio = Minio(
    endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_USER,
    secret_key=settings.MINIO_PASSWORD,
)
session = get_session()
create_tables()
seed_db()

storage_driver = StorageDriver(minio=minio, session=session)

# initialise model
model, processor = load_model()


def inference_images(image_set):
    household = image_set.camera.household.name
    dets_to_register = []
    annotated_images = []

    images = storage_driver.get_images_from_set(image_set)
    recieved_hour = image_set.received_date.hour
    for idx, image in enumerate(images):
        # Decide score thresh depending on hour of day
        if recieved_hour >= 21 or recieved_hour <= 6:
            min_det_score = 0.60
        else:
            min_det_score = 0.70
        detections = inference(
            model=model, processor=processor, image=image, min_score=min_det_score
        )
        for det in detections:
            dets_to_register.append(
                Detection(
                    image_id=image_set.intrusion_images[idx].id,
                    label=det["label"],
                    confidence=det["score"],
                    x_min=det["box"][0],
                    y_min=det["box"][1],
                    x_max=det["box"][2],
                    y_max=det["box"][3],
                )
            )

        # Annotate image
        if detections:
            annotated_images.append(
                annotate_detections(image=image, detections=detections)
            )

    logging.info(f"Inferenced images from {household} at {image_set.camera.caption}")
    return annotated_images, dets_to_register


def send_intrusion_message(
    max_detections: int,
    annotated_images: List[Image.Image],
    recipients: List[int],
    pretty_date: str,
    camera_location: str,
):

    # Do something with detection
    message = "Detected up to "
    if max_detections > 1:
        class_name = "people"
    else:
        class_name = "person"
    message = message + f"{max_detections} {class_name} at {camera_location}"
    message = message + f"\n{pretty_date}"

    logging.info(message)

    # Send message to recipients, retrying if there are any connectivity issues
    sent = False
    while not sent:
        try:
            asyncio.run(
                send_photo(
                    images=annotated_images,
                    image_caption=message,
                    recipients=recipients,
                )
            )
            sent = True
        except Exception as e:
            logging.warning(
                f"A telegram API connection occured:\n{e}\nRetrying in 120s..."
            )
            time.sleep(120)


# Infinite inference loop
while True:

    image_sets = storage_driver.get_uninferenced_image_sets()
    for image_set in image_sets:
        annotated_images, dets_to_register = inference_images(image_set=image_set)

        # Figure out the maximum number of people detected in any one image
        image_dets = {}
        for det in dets_to_register:
            if str(det.image_id) not in image_dets:
                image_dets[str(det.image_id)] = 0
            image_dets[str(det.image_id)] += 1
        max_detections = max(image_dets.values()) if dets_to_register else 0

        if len(dets_to_register) > 0:
            # Specify who is receiving a message if there is a detection.
            recipients = (
                [settings.USER_JOHN, settings.USER_S]
                if image_set.camera.household.name == "denning"
                else [settings.USER_A, settings.USER_R]
            )
            send_intrusion_message(
                max_detections=max_detections,
                annotated_images=annotated_images,
                recipients=recipients,
                pretty_date=image_set.pretty_date,
                camera_location=image_set.camera.caption,
            )

        # Commit finalised detections to DB and update image set inferenced state
        session.add_all(dets_to_register)
        session.commit()
        image_set.inferenced = True

    # zzzz
    time.sleep(10)
