from flask_mail import Message
from app import mail

def send_email(subject, sender, recipients, text_body, html_body, attach):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = html_body
    if attach:
        msg.attach(
            attach.filename,
            'application/octect-stream',
            attach.read()
        )
    mail.send(msg)