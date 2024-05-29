import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP server details
smtp_server = "smtp.gmail.com"
smtp_port = 587  # For TLS
sender_email = "anoj1810@gmail.com"
password = "utce zkpo jlen kaxq"


def send_email(email: str, subject: str, body: str):
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        server.sendmail(sender_email, email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
    finally:
        server.quit()


def send_verification_email(email: str, token: str):
    verification_link = f"http://localhost:8000/users/verify?token={token}"
    subject = "Verify your email"
    body = f"Hi,\n\nYour account been registered in our system. Please click the following link to verify your email:\n{verification_link}\n\nThank you!"
    send_email(email, subject, body)


def send_password_reset_email(email: str, token: str):
    reset_link = f"http://localhost:8000/reset-password?token={token}"
    subject = "Password Reset"
    body = f"Hi,\n\nYou have requested to reset your password. Please click on the following link to reset your password:\n{reset_link}\n\nIf you didn't request this, you can safely ignore this email.\n\nThank you!"
    send_email(email, subject, body)
