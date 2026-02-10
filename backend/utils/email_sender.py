import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_approval_email(to_email, ngo_name, ngo_id):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "VAANI – NGO Approved"

    body = f"""
Hello {ngo_name},

🎉 Your NGO has been approved on VAANI!

Your unique NGO ID is: {ngo_id}

You can now use this NGO ID to log in and post events.

Regards,
Team VAANI
"""
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
