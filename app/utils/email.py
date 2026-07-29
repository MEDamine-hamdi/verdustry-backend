import requests
from app.core.config import settings

FROM_EMAIL = "amie.bnr34@gmail.com"
FROM_NAME = "Verdustry"


def send_email(to_email: str, subject: str, body: str) -> None:
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": body,
        },
        timeout=10,
    )
    response.raise_for_status()