import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
async def send_email(to_email: str, subject: str, body: str, html_body: str = None):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        part1 = MIMEText(body, "plain")
        msg.attach(part1)
        if html_body:
            part2 = MIMEText(html_body, "html")
            msg.attach(part2)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
async def send_welcome_email(to_email: str, username: str):
    subject = "Welcome to Scholarly Platform"
    body = f"Dear {username},\n\nWelcome to Scholarly! We're excited to have you join our community of researchers.\n\nGet started by submitting your research papers and sharing your knowledge with the world.\n\nBest regards,\nScholarly Team"
    html_body = f"<h2>Welcome to Scholarly!</h2><p>Dear {username},</p><p>Welcome to Scholarly! We're excited to have you join our community of researchers.</p><p>Get started by submitting your research papers and sharing your knowledge with the world.</p><br><p>Best regards,<br>Scholarly Team</p>"
    return await send_email(to_email, subject, body, html_body)
