import smtplib
from email.message import EmailMessage

from app.config import settings


class EmailConfigurationError(RuntimeError):
    pass


class EmailDeliveryError(RuntimeError):
    pass


def ensure_email_configured() -> None:
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        raise EmailConfigurationError(
            "SMTP_HOST and SMTP_FROM_EMAIL must be configured"
        )


def send_password_reset_otp(
    recipient_email: str,
    recipient_name: str,
    otp: str,
) -> None:
    ensure_email_configured()

    message = EmailMessage()
    message["Subject"] = "Your SalesDesk password reset code"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient_email
    message.set_content(
        "\n".join(
            [
                f"Hello {recipient_name},",
                "",
                f"Your SalesDesk password reset code is: {otp}",
                (
                    "This code expires in "
                    f"{settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES} minutes."
                ),
                "",
                "If you did not request this change, you can ignore this email.",
            ]
        )
    )

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as smtp:
            smtp.ehlo()

            if settings.SMTP_USE_TLS:
                smtp.starttls()
                smtp.ehlo()

            if settings.SMTP_USERNAME:
                smtp.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD,
                )

            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError(
            "The password reset email could not be sent"
        ) from exc
