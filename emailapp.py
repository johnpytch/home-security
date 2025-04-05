import imaplib
import email
import time
from datetime import datetime
import logging
from PIL import Image
from io import BytesIO

from home_security.data.postgresql.database import get_session, create_tables, seed_db
from home_security.data.storage import StorageDriver
from home_security.data.minio.minio_client import Minio
from home_security.settings import settings

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

rec_sender = f'"{settings.REC_SENDER}" {settings.SENDER_ADDRESS}'
denn_sender = f'"{settings.DENN_SENDER}" {settings.SENDER_ADDRESS}'


def getEmails(result_bytes):
    msgs = []
    for num in result_bytes[0].split():
        _, data = con.fetch(num, "(RFC822)")
        msgs.append(data)
    return msgs


def conEmail():
    con = imaplib.IMAP4_SSL(settings.IMAP)
    con.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
    return con


# Set initial connection state
con = None

# Forevahhh
while True:
    try:

        # Reconnect if the connection was lost previously
        if not con:
            con = conEmail()
        status, messages = con.select("Inbox")
        for i in range(1, int(messages[0].decode("utf-8")) + 1):
            res, message = con.fetch(str(i), "(RFC822)")
            m = email.message_from_string(message[0][1].decode("utf-8"))
            sender = m.get("From")

            # Exclude unrecognised senders
            if sender not in [rec_sender, denn_sender]:
                con.store(str(i), "+FLAGS", "\\Deleted")
                logging.info(f"Deleted unrecognised email from {sender}")

            # Go through the email and extract images
            images = []
            for part in m.walk():
                if part["Content-type"] == "text/plain; charset=UTF-8":
                    body = part.get_payload()
                    date_time = body.split("\n")[3].split(" ")[5].split("\r")[0]

                    # Clean up the datetime from the email and make it look like YYYYMMDDHHMMSS
                    date_time = datetime.strptime(
                        date_time, "%Y-%m-%d,%H:%M:%S"
                    ).strftime("%Y%m%d%H%M%S")

                # if theres images there will be a filename
                filename = part.get_filename()
                if filename is not None:
                    camera_id = filename.split("-")[0]

                    # Get the image
                    image_bytes = part.get_payload(decode=True)
                    images.append(Image.open(BytesIO(image_bytes)))

            # Add images to postgres
            if images:
                storage_driver.add_image_set(
                    images=images, camera_id=camera_id, datetime_str=str(date_time)
                )

            # Delete the email
            con.store(str(i), "+FLAGS", "\\Deleted")
        time.sleep(30)

    except Exception as e:
        logging.error(e)
        logging.warning("Assumed network connectivity lost... Retrying in 60s")
        con = None
        time.sleep(60)
