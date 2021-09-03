from flask_mail import Message
from threading import Thread
import os
import smtplib
import sys
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config

def send(receiver, file, filename, date_time):
	subject = "Test: Bid Document"
	body = "This is an attachment from the E-bid form.\nFILENAME: " + filename + "\nDATE OF SUBMISSION: " + date_time
	sender_email = config('GMAIL_USER')
	receiver_email = receiver
	password = config('GMAIL_PASSWORD')

	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Subject"] = subject
	message["Bcc"] = sender_email  # Recommended for mass emails

	# Add body to email
	message.attach(MIMEText(body, "plain"))

	# Add file as application/octet-stream
	# Email client can usually download this automatically as attachment
	part = MIMEBase("application", "octet-stream")
	part.set_payload(file)

	# Encode file in ASCII characters to send by email    
	encoders.encode_base64(part)

	# Add header as key/value pair to attachment part
	part.add_header(
	    "Content-Disposition",
	    f"attachment; filename= {filename}",
	)

	# Add attachment to message and convert message to string
	message.attach(part)
	text = message.as_string()

	# Log in to server using secure context and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	    server.login(sender_email, password)
	    server.sendmail(sender_email, receiver_email, text)
