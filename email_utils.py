import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email: str, token: str):
    # Set up SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # For TLS
    sender_email = "anoj1810@gmail.com"
    password = "utce zkpo jlen kaxq"

    # Construct the message
    verification_link = f"http://localhost:8000/users/verify?token={token}"
    subject = "Verify your email"
    body = f"Hi,\n\nPlease verify your email by clicking on the following link:\n{verification_link}\n\nThank you!"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Connect to SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message.as_string())
    except Exception as e:
        # Log the exception instead of raising it
        print(f"Failed to send email to {email}: {e}")