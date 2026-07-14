import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


smtp_host = get_required_env("SMTP_HOST")
smtp_port = int(get_required_env("SMTP_PORT"))
smtp_username = get_required_env("SMTP_USERNAME").strip()

smtp_password = (
    get_required_env("SMTP_PASSWORD")
    .replace(" ", "")
    .replace("\u00a0", "")
    .replace("\r", "")
    .replace("\n", "")
    .replace("\t", "")
)

mail_from = get_required_env("MAIL_FROM")
mail_to_raw = get_required_env("MAIL_TO")

module = get_required_env("UPDATE_MODULE")
subject = get_required_env("UPDATE_SUBJECT")
update_file = Path(get_required_env("UPDATE_FILE"))

if not update_file.is_file():
    raise FileNotFoundError(f"Update file not found: {update_file}")

content = update_file.read_text(encoding="utf-8").strip()

if not content:
    raise RuntimeError(f"Update file is empty: {update_file}")

recipients = [
    address.strip()
    for address in (
        mail_to_raw
        .replace("\r", ",")
        .replace("\n", ",")
        .replace(";", ",")
        .split(",")
    )
    if address.strip()
]

if not recipients:
    raise RuntimeError("No valid recipients found in MAIL_TO")

message = EmailMessage()
message["From"] = mail_from
message["To"] = ", ".join(recipients)
message["Subject"] = f"[Hotmilk][{module}] {subject}"

message.set_content(
    f"""{content}

---
This notification was automatically sent from the Hotmilk GitHub repository:
https://github.com/baotong6/Hotmilk
"""
)

ssl_context = ssl.create_default_context()

if smtp_port == 465:
    with smtplib.SMTP_SSL(
        smtp_host,
        smtp_port,
        context=ssl_context,
        timeout=30,
    ) as server:
        server.login(smtp_username, smtp_password)
        server.send_message(message, to_addrs=recipients)

else:
    with smtplib.SMTP(
        smtp_host,
        smtp_port,
        timeout=30,
    ) as server:
        server.ehlo()
        server.starttls(context=ssl_context)
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.send_message(message, to_addrs=recipients)

print(f"Email sent successfully to {len(recipients)} recipient(s).")
