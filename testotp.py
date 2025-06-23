from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email, otp):
    # otp = generate_otp()

    sender_email = 'info@mathsenseacademy.in'  # Hostinger email
    password = 'suvadip#Math25'
    smtp_server = 'smtp.hostinger.com'
    smtp_port = 465  # SSL

    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It is valid for 10 minutes."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(e)
        print(f"Failed to send email: {e}")
        raise e
    finally:
        if server:
            server.quit()
    print("OTP SEND")
    return otp

send_otp_email('nathbubli@gmail.com', '158769')