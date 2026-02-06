import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        raise Exception("Email credentials missing")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)


def send_approval_email(to_email, ngo_name, temp_password):
    subject = "VAANI – NGO Approved"
    body = f"""
Hello {ngo_name},

Your NGO has been approved on VAANI.

Login Email: {to_email}
Temporary Password: {temp_password}

You can now post events using your NGO ID.

Regards,
Team VAANI
"""
    send_email(to_email, subject, body)


def send_rejection_email(to_email, ngo_name):
    subject = "VAANI – NGO Request Rejected"
    body = f"""
Hello {ngo_name},

Unfortunately, your NGO request was not approved.

Regards,
Team VAANI
"""
    send_email(to_email, subject, body)
