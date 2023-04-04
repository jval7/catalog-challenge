import smtplib
from email.message import EmailMessage
from typing import List

from decouple import config

PORT = config("PORT")
SMTP_SERVER = config("SMTP_SERVER")
SENDER_EMAIL = config("SENDER_EMAIL")
RECEIVER_EMAIL = config("RECEIVER_EMAIL")
PASSWORD = config("PASSWORD")


class AbstractNotification:
    @staticmethod
    def send(addressees: List, subject: str, body: str):
        raise NotImplementedError


class EmailNotification:
    @staticmethod
    def send(addressees: List, subject: str, body: str):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(addressees)
        msg.set_content(body)

        with smtplib.SMTP_SSL(SMTP_SERVER, PORT, timeout=3) as smtp:
            smtp.login(SENDER_EMAIL, PASSWORD)
            smtp.send_message(msg)
