import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


smtp_host = required_env("SMTP_HOST")
smtp_port = int(required_env("SMTP_PORT"))
smtp_username = required_env("SMTP_USERNAME")
smtp_password = required_env("SMTP_PASSWORD")

mail_from = required_env("MAIL_FROM")
mail_to = required_env("MAIL_TO")

module = required_env("UPDATE_MODULE")
subject = required_env("UPDATE_SUBJECT")
update_file = Path(required_env("UPDATE_FILE"))

repository_url = required_env("REPOSITORY_URL")
commit_sha = required_env("COMMIT_SHA")

if not update_file.is_file():
    raise FileNotFoundError(f"Update file does not exist: {update_file}")

content = update_file.read_text(encoding="utf-8").strip()

if not content:
    raise RuntimeError(f"Update file is empty: {update_file}")

message = EmailMessage()
message["From"] = mail_from
message["To"] = mail_to
message["Subject"] = f"[Hotmilk][{module}] {subject}"

message.set_content(
    f"""{content}

---
Module: {module}
Repository: {repository_url}
Version: {commit_sha[:7]}
"""
)

ssl_context = ssl.create_default_context()

if smtp_port == 465:
    with smtplib.SMTP_SSL(
        smtp_host,
        smtp_port,
        context=ssl_context,
    ) as server:
        server.login(smtp_username, smtp_password)
        server.send_message(message)
else:
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls(context=ssl_context)
        server.login(smtp_username, smtp_password)
        server.send_message(message)

print("Hotmilk group notification sent successfully.")
