import imaplib
import email
import os
import time
import json
from datetime import datetime

# Get env json variables
with open("./env.json", "r") as file:
    env_file = json.load(file)
env_email = env_file.get("EMAIL")
env_households = env_file.get('HOUSEHOLDS')

DENN = env_households.get('DENN')
REC = env_households.get('REC')
user = env_email.get("USER")
password = env_email.get("PASSWORD")
imap_url = env_email.get("IMAP")
REC_SENDER = env_email.get("REC_SENDER")
DENN_SENDER = env_email.get("DENN_SENDER")
SENDER_ADDRESS = env_email.get("SENDER_ADDRESS")
rec_sender = f'"{REC_SENDER}" {SENDER_ADDRESS}'
denn_sender = f'"{DENN_SENDER}" {SENDER_ADDRESS}'


def getEmails(result_bytes):
    msgs = []
    for num in result_bytes[0].split():
        _, data = con.fetch(num, "(RFC822)")
        msgs.append(data)
    return msgs


def conEmail():
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user, password)
    return con


con = conEmail()
while True:
    try:
        status, messages = con.select("Inbox")
        for i in range(1, int(messages[0].decode("utf-8")) + 1):
            res, message = con.fetch(str(i), "(RFC822)")
            m = email.message_from_string(message[0][1].decode("utf-8"))
            sender = m.get("From")

            # Which household is it coming from?
            if sender == rec_sender:
                household = REC
            elif sender == denn_sender:
                household = DENN

            # Only process the email if the sender is recognised as rectory or denning
            if sender in [rec_sender, denn_sender]:

                # Go through the email and extract images
                for part in m.walk():
                    if part["Content-type"] == "text/plain; charset=UTF-8":
                        body = part.get_payload()
                        date_time = body.split("\n")[3].split(" ")[5].split("\r")[0]

                        # Clean up the datetime from the email and make it look like YYYYMMDDHHMMSS
                        date_time = datetime.strptime(
                            date_time, "%Y-%m-%d,%H:%M:%S"
                        ).strftime("%Y%m%d%H%M%S")

                    filename = part.get_filename()
                    if filename is not None:

                        savefilename = filename.split(".")[0] + "_" + date_time + ".jpg"
                        path = f"../images/new_images/{household}/" + savefilename

                        if not os.path.isfile(path):
                            # Save the image
                            with open(path, "wb") as f:
                                f.write(part.get_payload(decode=True))

                            print("Saved image " + savefilename)
            con.store(str(i), "+FLAGS", "\\Deleted")
        print("Sleeping for 60s")
        time.sleep(30)
    except:
        print("Assumed network connectivity lost... Retrying in 60s")
        time.sleep(120)
        con = conEmail()
        pass
