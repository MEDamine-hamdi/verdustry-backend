import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

FROM_EMAIL = "contact@verdustry.com"
FROM_NAME = "Verdustry"


def send_email(to_email: str, subject: str, body: str) -> None:
    message = MIMEText(body, "html")
    message["Subject"] = subject
    message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    message["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [to_email], message.as_string())	
